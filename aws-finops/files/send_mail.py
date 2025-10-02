import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()


def verify_email_identity(email_address):
    """Verify if an email identity is verified in SES

    :param email_address: Email address to verify
    :return: Boolean indicating if email is verified
    """
    try:
        ses_client = boto3.client('ses', region_name='us-east-1')
        response = ses_client.get_identity_verification_attributes(Identities=[email_address])

        verification_status = response.get('VerificationAttributes', {}).get(email_address, {}).get('VerificationStatus')

        if verification_status == 'Success':
            logger.info(f'Email identity {email_address} is verified')
            return True
        else:
            logger.warning(f'Email identity {email_address} is not verified. Status: {verification_status}')
            return False

    except ClientError as e:
        logger.error(f'Error verifying email identity: {str(e)}')
        return False


def get_email_body(deleted_resources, skip_delete_resources, notify_resources, check_resources):
    """Generate HTML email body with resource cleanup results

    :param deleted_resources: List of tuples (resource_type, resource_id) that were deleted
    :param skip_delete_resources: List of tuples (resource_type, resource_id) that were skipped (dry run)
    :param notify_resources: List of tuples (resource_type, resource_id) that need attention
    :param check_resources: List of tuples (resource_type, resource_id) that failed deletion
    :return: HTML formatted email body
    """
    html_body = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 25px;
                border-left: 4px solid #3498db;
                padding-left: 10px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            }
            th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #e8f4f8;
            }
            .summary {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .summary-item {
                display: inline-block;
                margin: 10px 20px 10px 0;
                padding: 10px 15px;
                background-color: white;
                border-radius: 3px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .count {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
            .deleted { color: #27ae60; }
            .skipped { color: #f39c12; }
            .failed { color: #e74c3c; }
            .notify { color: #9b59b6; }
            .footer {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #bdc3c7;
                font-size: 12px;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <h1>AWS FinOps Resource Cleanup Report</h1>

        <div class="summary">
            <h2>Summary</h2>
    """

    # Add summary counts
    html_body += f"""
            <div class="summary-item">
                <div>Deleted/Stopped</div>
                <div class="count deleted">{len(deleted_resources)}</div>
            </div>
            <div class="summary-item">
                <div>Skipped (Dry Run)</div>
                <div class="count skipped">{len(skip_delete_resources)}</div>
            </div>
            <div class="summary-item">
                <div>Failed</div>
                <div class="count failed">{len(check_resources)}</div>
            </div>
            <div class="summary-item">
                <div>Needs Attention</div>
                <div class="count notify">{len(notify_resources)}</div>
            </div>
        </div>
    """

    # Skipped resources (Dry Run)
    if skip_delete_resources:
        html_body += """
        <h2>Resources to be Deleted/Stopped (Dry Run Mode)</h2>
        <table>
            <tr>
                <th>Resource Type</th>
                <th>Resource ID / Description</th>
            </tr>
        """
        for resource_type, resource_id in skip_delete_resources:
            html_body += f"""
            <tr>
                <td><strong>{resource_type}</strong></td>
                <td>{resource_id}</td>
            </tr>
            """
        html_body += "</table>"

    # Deleted resources
    if deleted_resources:
        html_body += """
        <h2>Successfully Deleted/Stopped Resources</h2>
        <table>
            <tr>
                <th>Resource Type</th>
                <th>Resource ID / Description</th>
            </tr>
        """
        for resource_type, resource_id in deleted_resources:
            html_body += f"""
            <tr>
                <td><strong>{resource_type}</strong></td>
                <td>{resource_id}</td>
            </tr>
            """
        html_body += "</table>"

    # Failed resources
    if check_resources:
        html_body += """
        <h2 style="color: #e74c3c;">Failed to Delete/Stop (Action Required)</h2>
        <table>
            <tr>
                <th>Resource Type</th>
                <th>Resource ID</th>
            </tr>
        """
        for resource_type, resource_id in check_resources:
            html_body += f"""
            <tr>
                <td><strong>{resource_type}</strong></td>
                <td>{resource_id}</td>
            </tr>
            """
        html_body += "</table>"

    # Resources needing attention
    if notify_resources:
        html_body += """
        <h2 style="color: #9b59b6;">Resources Needing Attention</h2>
        <table>
            <tr>
                <th>Resource Type</th>
                <th>Resource ID</th>
            </tr>
        """
        for resource_type, resource_id in notify_resources:
            html_body += f"""
            <tr>
                <td><strong>{resource_type}</strong></td>
                <td>{resource_id}</td>
            </tr>
            """
        html_body += "</table>"

    # No resources found
    if not (deleted_resources or skip_delete_resources or check_resources or notify_resources):
        html_body += """
        <div class="summary">
            <p><strong>No resources found for cleanup in any category.</strong></p>
            <p>All resources are either in use or protected by tags.</p>
        </div>
        """

    html_body += """
        <div class="footer">
            <p>This is an automated report from AWS FinOps Resource Cleanup Lambda function.</p>
            <p>For questions or concerns, please contact your DevOps team.</p>
        </div>
    </body>
    </html>
    """

    return html_body


def send_html_email(from_address, to_address, subject, html_body):
    """Send HTML formatted email using SES

    :param from_address: Sender email address (must be verified in SES)
    :param to_address: Recipient email address
    :param subject: Email subject
    :param html_body: HTML formatted email body
    """
    ses_client = boto3.client('ses', region_name='us-east-1')

    try:
        response = ses_client.send_email(
            Source=from_address,
            Destination={
                'ToAddresses': [to_address]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        logger.info(f'Email sent successfully. Message ID: {response["MessageId"]}')
        return True

    except ClientError as e:
        logger.error(f'Error sending email: {str(e)}')
        return False


def send_email(from_address, to_address, deleted_resources, skip_delete_resources, notify_resources, check_resources):
    """Main function to send email notification about resource cleanup

    :param from_address: Sender email address
    :param to_address: Recipient email address
    :param deleted_resources: List of deleted resources
    :param skip_delete_resources: List of skipped resources (dry run)
    :param notify_resources: List of resources needing attention
    :param check_resources: List of failed deletions
    """
    subject = "AWS FinOps: Resource Cleanup Report"
    verified = verify_email_identity(from_address)

    if verified:
        html_body = get_email_body(deleted_resources, skip_delete_resources, notify_resources, check_resources)
        send_html_email(from_address, to_address, subject, html_body)
        logger.info("Email sent successfully")
    else:
        logger.warning("Warning: Email address is not verified yet, unable to send email notification.")
        logger.info("Please verify the email address in SES console: https://console.aws.amazon.com/ses/")
