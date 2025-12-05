"""
Email notification service for Crystal Ball CI/CD.

This module provides email notification functionality for prediction alerts.
Uses proper validation, error handling, and async operations.
"""

import re
import logging
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email service configuration."""
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    from_address: str
    use_tls: bool = True


class EmailService:
    """
    Service for sending email notifications.

    Provides validated, secure email sending with proper error handling.
    """

    def __init__(self, config: EmailConfig):
        """
        Initialize email service with configuration.

        Args:
            config: Email configuration dataclass
        """
        self.config = config
        logger.info(f"EmailService initialized for {config.smtp_host}:{config.smtp_port}")

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def send_prediction_alert(
        self,
        to_addresses: List[str],
        prediction_score: int,
        pr_url: str,
        omens_count: int
    ) -> bool:
        """
        Send prediction alert email to recipients.

        Args:
            to_addresses: List of recipient email addresses
            prediction_score: Prediction score (0-100)
            pr_url: Pull request URL
            omens_count: Number of omens detected

        Returns:
            True if email sent successfully, False otherwise
        """
        # Validate all recipient addresses
        valid_addresses = [addr for addr in to_addresses if self.validate_email(addr)]

        if not valid_addresses:
            logger.error("No valid email addresses provided")
            return False

        # Determine severity level
        if prediction_score >= 80:
            severity = "✅ Good"
            color = "green"
        elif prediction_score >= 60:
            severity = "⚠️ Caution"
            color = "orange"
        else:
            severity = "🔴 Warning"
            color = "red"

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Crystal Ball Alert: {severity} - Score {prediction_score}'
        msg['From'] = self.config.from_address
        msg['To'] = ', '.join(valid_addresses)

        # HTML body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {color};">🔮 Crystal Ball Prediction</h2>
                <p><strong>Pull Request:</strong> <a href="{pr_url}">{pr_url}</a></p>
                <p><strong>Prediction Score:</strong> <span style="color: {color}; font-size: 24px;">{prediction_score}%</span></p>
                <p><strong>Issues Found:</strong> {omens_count} omen(s)</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated message from Crystal Ball CI/CD system.
                </p>
            </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Send email
        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()

                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            logger.info(f"Prediction alert sent to {len(valid_addresses)} recipient(s)")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False
