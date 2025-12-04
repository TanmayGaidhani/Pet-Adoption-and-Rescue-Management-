from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend
import ssl

class CustomEmailBackend(DjangoEmailBackend):
    """
    Custom email backend to fix Python 3.12 compatibility issue
    with Django's SMTP backend starttls() method
    """
    def open(self):
        if self.connection:
            return False

        try:
            self.connection = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            self.connection.ehlo()
            
            if self.use_tls:
                # Fix for Python 3.12 - use context parameter instead of keyfile/certfile
                context = ssl.create_default_context()
                if self.ssl_certfile:
                    context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
                self.connection.starttls(context=context)
                self.connection.ehlo()
                
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
