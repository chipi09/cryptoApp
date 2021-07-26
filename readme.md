# Instalacion

Instalar las dependencias del fichero requerimientos.txt
```
pip install -r requerimientos.txt
```
Ejecutar el script `\env\Scripts\activate`

Ejecutar la instrucción `flask run` 

# Tablas utilizadas
```
CREATE TABLE "MOVIMIENTOS" (
	"id"	INTEGER NOT NULL UNIQUE,
	"date"	TEXT,
	"time"	TEXT,
	"moneda_from"	TEXT,
	"cantidad_from"	REAL,
	"moneda_to"	TEXT,
	"cantidad_to"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
)
```
