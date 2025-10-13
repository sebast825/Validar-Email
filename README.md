# Validador de Emails (SMTP/DNS)

Herramienta Python para verificar la validez de direcciones de email mediante:

- Sintaxis (regex)
- DNS (registros MX)
- SMTP (comprobación de buzón real)
- Catch-All (Detecta si el dominio acepta todos los emails aunque no existan, lo que indica posibles resultados poco fiables)

## Características clave
- Multihilo: Procesamiento paralelo con N hilos.

- Tolerante a fallos: Manejo de errores DNS/SMTP (timeouts, bloqueos antispam).

## Reportes

- Resumen estadístico en terminal.

- Exportación a Excel con pestañas por estado.

- Optimizado: Delays configurables para evitar bloqueos (Gmail/Outlook).

------------------------------------------------------------------------------------------------
## Como usar la app

- Crear un archivo emails.txt que tenga un email por linea, al correr el programa aanalizara uno por uno

--------------------------------------------------------------------------------------------------

## Explicación de cada resultado

✅ Válido
Los emails existen y el servidor MX aceptó la dirección.

⚠️ Todos los MX fallaron 
Causa: Ninguno de los servidores de correo (MX) del dominio respondió correctamente.

- Posibles razones:
-Dominio existe pero no tiene servidores de correo configurados.
-Firewalls bloquean conexiones SMTP externas.
-Problemas temporales de red.

⚠️ Error SMTP: Connection unexpectedly closed (timeout)

Causa: El servidor no respondió en el tiempo establecido (timeout=10).
Solución: Aumentar timeout o reintentar.

⚠️ Error SMTP: [WinError 10054/10053]
10054: "Host remoto forzó el cierre" → El servidor cortó la conexión abruptamente (antispam).
10053: "Software local cerró la conexión" → Problema en tu red o firewall.
Solución: Añadir time.sleep() más largo entre conexiones.

❌ Dominio no existe 
El dominio (parte después de @) no está registrado o no tiene DNS válidos.

❌ Sintaxis inválida 
El formato del email no cumple con usuario@dominio.extensión (ej: usuario@.com).

⚠️ Errores temporales (450/454)
450: "Mailbox busy" → Intenta más tarde.
454: "Temporary authentication failure" → Problema de configuración del servidor.
