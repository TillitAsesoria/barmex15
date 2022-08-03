from odoo import models,fields

class CredentialsAD(models.Model):
    _name = "credenciales"
    _description = 'agregar documentos para el autenticación del almacen digital'
    # un solo registro por RFC
    name = fields.Char("RFC")
    password_fiel = fields.Char("Contraseña",help="campo solo para anotar contraseña")
    cer_fiel_name = fields.Char("Certificado")
    cer_fiel = fields.Binary(string="Archivo Certificado",attachment=False)
    key_fiel_name = fields.Char("Key")
    key_fiel = fields.Binary(string="Archivo Key",attachment=False)

