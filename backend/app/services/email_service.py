"""
Email service for sending emails
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SMTP_USERNAME", "")
        self.sender_password = os.getenv("SMTP_PASSWORD", "")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """
        Send password reset email to user
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: User's name
        """
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Reset Request"
        msg["From"] = self.sender_email
        msg["To"] = to_email
        
        # Create the reset link
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # Create the HTML version of your message
        html = f"""
        <html>
          <body>
            <p>Hi {user_name},</p>
            <p>You have requested to reset your password. Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Thanks,<br>The jobSee Team</p>
          </body>
        </html>
        """
        
        # Create plain text version
        text = f"""
        Hi {user_name},
        
        You have requested to reset your password. Use the link below to reset your password:
        
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Thanks,
        The jobSee Team
        """
        
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        # Add HTML/plain-text parts to MIMEMultipart message
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

# Create a global instance
email_service = EmailService()