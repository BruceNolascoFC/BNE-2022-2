# BNE-2022-2
Proyecto Bases de Datos no Estructuradas

Requiere una instancia de REDIS corriendo en el puerto 6379. 
`sudo docker run -p 6379:6379 -d --name one redis`

Y streamlit:
`streamlit run interfaz.py `

-------
Proyecto 2
Requiere de los drivers de Cassandra instalados.
Requiere que el certificado de conexión esté en el mismo directorio.

`streamlit run interfaz2.py `

En caso de error reinciar (_rerun_) la interfaz.

