from flask import render_template

class EmailLogic:
    @classmethod
    def enviar_bienvenida_registro(cls, persona):
        try:
            html = render_template('emails/bienvenida.html', persona=persona)
            from app import enviar_correo_async
            enviar_correo_async("¡Bienvenido a VL Alojamientos!", [persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar email de bienvenida: {e}")

    @classmethod
    def enviar_confirmacion_reserva(cls, reserva):
        try:
            html = render_template('emails/reserva_confirmada.html', reserva=reserva)
            from app import enviar_correo_async
            enviar_correo_async(f"Confirmación de Reserva #{reserva.id}", [reserva.persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar email de reserva: {e}")

    @classmethod
    def enviar_bienvenida_checkin(cls, reserva):
        try:
            html = render_template('emails/checkin_bienvenida.html', reserva=reserva)
            from app import enviar_correo_async
            enviar_correo_async("¡Disfruta tu estadía!", [reserva.persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar email de check-in: {e}")

    @classmethod
    def enviar_recibo_checkout(cls, reserva, total_consumos, total_general):
        try:
            html = render_template('emails/checkout_recibo.html',
                                   reserva=reserva,
                                   total_consumos=total_consumos,
                                   total_general=total_general)
            from app import enviar_correo_async
            enviar_correo_async("Comprobante de Check-out", [reserva.persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar email de check-out: {e}")

    @classmethod
    def enviar_notificacion_cancelacion(cls, reserva):
        try:
            html = render_template('emails/reserva_cancelada.html', reserva=reserva)
            from app import enviar_correo_async
            enviar_correo_async("Cancelación de Reserva", [reserva.persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar email de cancelación: {e}")

    @classmethod
    def enviar_recordatorio_manana(cls, reserva):
        try:
            html = render_template('emails/recordatorio.html', reserva=reserva)
            from app import enviar_correo_async
            enviar_correo_async("Recordatorio de tu reserva para mañana", [reserva.persona.email], html)
        except Exception as e:
            print(f"No se pudo enviar recordatorio: {e}")

    @classmethod
    def enviar_email_recuperacion(cls, persona, token):
        from flask import url_for
        url_recuperacion = url_for('restablecer_contrasena', token=token, _external=True)
        html = render_template('emails/recuperar_password.html',
                               persona=persona,
                               url=url_recuperacion)
        from app import enviar_correo_async
        enviar_correo_async("Recuperación de Contraseña", [persona.email], html)