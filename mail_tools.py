import smtplib
from email.mime.text import MIMEText

from jinja2 import Template

def generate_html(title, items):
    if not items or len(items) == 0:
        return

    html_template = """
        <ul>
            {% for item in items %}
                <li><a href="{{ item.href }}">{{ item.name }}</a></li>
            {% endfor %}
        </ul>
    """
    template = Template(html_template)
    html_code = template.render(items=items)
    return send_mail(["350821495@qq.com"], title, html_code)


def send_mail(to_list, sub, content):
    mail_host = "smtp.qq.com"
    mail_user = "1525496905@qq.com"
    mail_pass = "eqpbgqmnksyqggdd"

    me = f"<{mail_user}>"
    msg = MIMEText(content, _subtype="html", _charset="utf-8")
    msg["Subject"] = sub
    msg["From"] = me
    msg["To"] = ",".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False


if __name__ == "__main__":
    generate_html("简书汇总", None)
