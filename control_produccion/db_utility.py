import psycopg2


# constants
VAL_INDEX = 0
VAL_VALUE = 1

# indeces of rows read
INDEX_CLIENT = 0
INDEX_OP_NUMBER = 1
INDEX_QUANTITY = 2
INDEX_SHEETS = 3
INDEX_MACHINE = 4
INDEX_DESCRIPTION = 5
INDEX_IMPRESION_T = 6
INDEX_IMPRESION_TR = 7
INDEX_BARNIZ_T = 8
INDEX_BARNIZ_TR = 9
INDEX_SIZADO = 10
INDEX_PERFORADO = 11
INDEX_TROQUELADO = 12
INDEX_DOBLADO = 13
INDEX_ESPIRAL = 14
INDEX_PEGADO = 15
INDEX_DESPUNTADO = 16
INDEX_BLOCADO = 17
INDEX_EMPALMADO = 18
INDEX_OJETEADO = 19
INDEX_SENSE_T = 20
INDEX_SENSE_TR = 21
INDEX_PLASTICO_T = 22
INDEX_PLASTICO_TR = 23
INDEX_PLASTICO_MATE = 24
INDEX_PLASTICO_BRILLANTE = 25
INDEX_FOIL_T = 26
INDEX_FOIL_TR = 27
INDEX_LOMO = 28
INDEX_GRAPA = 29
INDEX_CORTE = 30
INDEX_DUE_DATE = 31

# values for stored indices
VALUE_PROCESSES = 'processes'
VALUE_CLIENT = 'client'
VALUE_OP_NUMBER = 'op_number'
VALUE_QUANTITY = 'quantity'
VALUE_SHEETS = 'sheets'
VALUE_MACHINE = 'machine'
VALUE_DESCRIPTION = 'description'
VALUE_IMPRESION_T = 'Impresión Tiro'
VALUE_IMPRESION_TR = 'Impresión Tiro/Retiro'
VALUE_BARNIZ_T = 'Barniz Tiro'
VALUE_BARNIZ_TR = 'Barniz Tiro/Retiro'
VALUE_SIZADO = 'Sizado'
VALUE_PERFORADO = 'Perforado'
VALUE_TROQUELADO = 'Troquelado'
VALUE_DOBLADO = 'Doblado'
VALUE_ESPIRAL = 'Espiral'
VALUE_PEGADO = 'Pegado'
VALUE_DESPUNTADO = 'Despuntado'
VALUE_BLOCADO = 'Blocado'
VALUE_EMPALMADO = 'Empalmado'
VALUE_OJETEADO = 'Ojeteado'
VALUE_SENSE_T = 'Sense Tiro'
VALUE_SENSE_TR = 'Sense Tiro/Retiro'
VALUE_PLASTICO_T = 'Plástico Tiro'
VALUE_PLASTICO_TR = 'Plástico Tiro/Retiro'
VALUE_PLASTICO_MATE = 'Plástico Mate'
VALUE_PLASTICO_BRILLANTE = 'Plástico Brillante'
VALUE_FOIL_T = 'Foil Tiro'
VALUE_FOIL_TR = 'Foil Tiro/Retiro'
VALUE_LOMO = 'Lomo'
VALUE_GRAPA = 'Grapa'
VALUE_CORTE = 'Corte'
VALUE_DUE_DATE = 'Fecha Entrega'

# list of tuples of index, name-of-field
INDICES = [
    (INDEX_CLIENT, VALUE_CLIENT),  # index 0
    (INDEX_OP_NUMBER, VALUE_OP_NUMBER),  # index 1
    (INDEX_QUANTITY, VALUE_QUANTITY),  # index 2
    (INDEX_SHEETS, VALUE_SHEETS),  # index 3
    (INDEX_MACHINE, VALUE_MACHINE),  # index 4
    (INDEX_DESCRIPTION, VALUE_DESCRIPTION),  # index 5
    (INDEX_IMPRESION_T, VALUE_IMPRESION_T),  # index 6
    (INDEX_IMPRESION_TR, VALUE_IMPRESION_TR),  # index 7
    (INDEX_BARNIZ_T, VALUE_BARNIZ_T),  # index 8
    (INDEX_BARNIZ_TR, VALUE_BARNIZ_TR),  # index 9
    (INDEX_SIZADO, VALUE_SIZADO),  # index 10
    (INDEX_PERFORADO, VALUE_PERFORADO),  # index 11
    (INDEX_TROQUELADO, VALUE_TROQUELADO),  # index 12
    (INDEX_DOBLADO, VALUE_DOBLADO),  # index 13
    (INDEX_ESPIRAL, VALUE_ESPIRAL),  # index 14
    (INDEX_PEGADO, VALUE_PEGADO),  # index 15
    (INDEX_DESPUNTADO, VALUE_DESPUNTADO),  # index 16
    (INDEX_BLOCADO, VALUE_BLOCADO),  # index 17
    (INDEX_EMPALMADO, VALUE_EMPALMADO),  # index 18
    (INDEX_OJETEADO, VALUE_OJETEADO),  # index 19
    (INDEX_SENSE_T, VALUE_SENSE_T),  # index 20
    (INDEX_SENSE_TR, VALUE_SENSE_TR),  # index 21
    (INDEX_PLASTICO_T, VALUE_PLASTICO_T),  # index 22
    (INDEX_PLASTICO_TR, VALUE_PLASTICO_TR),  # index 23
    (INDEX_PLASTICO_MATE, VALUE_PLASTICO_MATE),  # index 24
    (INDEX_PLASTICO_BRILLANTE, VALUE_PLASTICO_BRILLANTE),  # index 25
    (INDEX_FOIL_T, VALUE_FOIL_T),  # index 26
    (INDEX_FOIL_TR, VALUE_FOIL_TR),  # index 27
    (INDEX_LOMO, VALUE_LOMO),  # index 28
    (INDEX_GRAPA, VALUE_GRAPA),  # index 29
    (INDEX_CORTE, VALUE_CORTE),  # index 30
    (INDEX_DUE_DATE, VALUE_DUE_DATE),  # index 31
]
# db information
DATABASE_NAME = "sunhive"
USER_NAME = "reportedh"
PASSWORD = "digitalh16"
HOST_NAME = "192.168.0.2"
PORT_NUMBER = "5432"

# main query
QUERY = (
    "select op.\"NombreCliente\" as \"Cliente\", op.\"Numero\"||'-'||opp.\"Linea\" as \"Numero\", min(opp.\"Cantidad\") as \"Cantidad\", min(opm.\"NumeroPliegosPrensa\")+ min(opm.\"VentajaPliegosPrensa\") as \"TotalPP\", "
    "min(mi.\"Descripcion\") as \"MaquinaImpresion\", min(opp.\"DescripcionProducto\") as \"DescripcionMaterial\", "
    "max(case when cop.\"CodigoProceso\" in (2,6) then 'X' else '' end) as \"ImpresionTiro\", "
    "max(case when cop.\"CodigoProceso\" in (1,7) then 'X' else '' end) as \"ImpresionTiroRetiro\", "
    "max(case when cop.\"CodigoProceso\"=3 then 'X' else '' end) as \"BarnizTiro\", "
    "max(case when cop.\"CodigoProceso\"=4 then 'X' else '' end) as \"BarnizTiroRetiro\", "
    "max(case when cop.\"CodigoProceso\"=68 then 'X' else '' end) as \"Sizado\", "
    "max(case when cop.\"CodigoProceso\"=71 then 'X' else '' end) as \"Perforado\", "
    "max(case when opt.\"CodigoOrdenProduccion\" is not null then 'X' else '' end) as \"Troquelado\", "
    "max(case when cop.\"CodigoProceso\"=8 then 'X' else '' end) as \"Doblado\", "
    "max(case when cop.\"CodigoProceso\"=75 then 'X' else '' end) as \"Espiral\", "
    "max(case when opemp.\"CodigoOrdenProduccion\" is not null then 'X' else '' end) as \"Pegado\", "
    "max(case when cop.\"CodigoProceso\" in (26,27) then 'X' else '' end) as \"Despuntado\", "
    "max(case when opblocado.\"CodigoOrdenProduccion\" is not null  then 'X' else '' end) as \"Blocado\", "
    "max(case when opempalmado.\"CodigoOrdenProduccion\" is not null  then 'X' else '' end) as \"Empalmar\", "
    "max(case when opojeteado.\"CodigoOrdenProduccion\" is not null  then 'X' else '' end) as \"Ojeteado\", "
    "max(case when cop.\"CodigoProceso\"=57 then 'X' else '' end) as \"SensefectTiro\", "
    "max(case when cop.\"CodigoProceso\"=74 then 'X' else '' end) as \"SensefectTiroRetiro\", "
    "max(case when cop.\"CodigoProceso\" in (66,18,16,72,32,53,58,62,64) then 'X' else '' end) as \"PlasticoTiro\", "
    "max(case when cop.\"CodigoProceso\" in (13,67,19,17,73,33,54,59,63,65) then 'X' else '' end) as \"PlasticoTiroRetiro\", "
    "max(case when cop.\"CodigoProceso\" in (16,17,32,33,58,59,72,73) then 'X' else '' end) as \"PlasticoMate\", "
    "max(case when cop.\"CodigoProceso\" in (18,19,12,13,53,54,62,63,64,65,66,67) then 'X' else '' end) as \"PlasticoBrillante\", "
    "max(case when cop.\"CodigoProceso\" in (39,43,25,35,37,45,41,47) then 'X' else '' end) as \"FoilTiro\", "
    "max(case when cop.\"CodigoProceso\" in (40,44,34,36,38,46,42,48) then 'X' else '' end) as \"FoilTiroRetiro\", "
    "max(case when cop.\"CodigoProceso\"=11 then 'X' else '' end) as \"Lomo\", "
    "max(case when cop.\"CodigoProceso\"=10 then 'X' else '' end) as \"Grapa\", "
    "max(case when cop.\"CodigoProceso\"=5 then 'X' else '' end) as \"Corte\", "
    "op.\"FechaRequerida\" "
    "from \"Produccion\".\"OrdenesProduccion\" op "
    "inner join \"Produccion\".\"OrdenesProduccionProductos\" opp on "
    "op.\"Codigo\"=opp.\"CodigoOrdenProduccion\" "
    "inner join \"Produccion\".\"OrdenesProduccionMateriales\" opm on "
    "op.\"Codigo\" = opm.\"CodigoOrdenProduccion\" and "
    "opm.\"Linea\" = opp.\"Linea\" "
    "inner join \"Produccion\".\"OrdenesProduccionOffset\" opo on "
    "op.\"Codigo\" = opo.\"CodigoOrdenProduccion\" and "
    "opo.\"Linea\" = opp.\"Linea\" "
    "inner join \"Cotizaciones\".\"MaquinasImpresion\" mi on "
    "opo.\"CodigoMaquinaImpresion\" = mi.\"Codigo\" "
    "inner join \"Cotizaciones\".\"MaterialesImpresion\" mti on "
    "mti.\"Codigo\" = opm.\"CodigoMaterial\" "
    "left outer join \"Produccion\".\"OrdenesProduccionOtrosProcesos\" ope on "
    "op.\"Codigo\"=ope.\"CodigoOrdenProduccion\" "
    "and ope.\"Linea\" = opp.\"Linea\" "
    "left outer join \"Cotizaciones\".\"CotizacionesProductosOtrosProcesos\" cop on "
    "cop.\"CodigoCotizacion\"=op.\"CodigoCotizacion\" and "
    "cop.\"LineaProducto\"=ope.\"Linea\"-1 and "
    "cop.\"LineaProceso\"=ope.\"LineaProceso\" and "
    "cop.\"LineaCantidad\"=op.\"LineaCantidad\"  "
    "left outer join \"Produccion\".\"OrdenesProduccionTipografia\" opt on "
    "op.\"Codigo\"=opt.\"CodigoOrdenProduccion\" "
    "and opt.\"Linea\" = opp.\"Linea\" "
    "and \"CodigoTipoTipografia\"=1 "
    "left outer join \"Produccion\".\"OrdenesProduccionEmpaque\" opemp on "
    "op.\"Codigo\"=opemp.\"CodigoOrdenProduccion\" "
    "and opemp.\"Linea\" = opp.\"Linea\" "
    "and opemp.\"CodigoProcesoEmpaque\" in (1,2) "
    "left outer join \"Produccion\".\"OrdenesProduccionEmpaque\" opblocado on "
    "op.\"Codigo\"=opblocado.\"CodigoOrdenProduccion\" "
    "and opblocado.\"Linea\" = opp.\"Linea\" "
    "and opblocado.\"CodigoProcesoEmpaque\" in (9) "
    "left outer join \"Produccion\".\"OrdenesProduccionEmpaque\" opempalmado on "
    "op.\"Codigo\"=opempalmado.\"CodigoOrdenProduccion\" "
    "and opempalmado.\"Linea\" = opp.\"Linea\" "
    "and opempalmado.\"CodigoProcesoEmpaque\" in (4) "
    "left outer join \"Produccion\".\"OrdenesProduccionEmpaque\" opojeteado on "
    "op.\"Codigo\"=opojeteado.\"CodigoOrdenProduccion\" "
    "and opojeteado.\"Linea\" = opp.\"Linea\" "
    "and opojeteado.\"CodigoProcesoEmpaque\" in (15) "
    "where "
    "op.\"Estado\" in ('P','R') "
    "and op.\"FechaCreacion\" > '20151001' "
    "group by op.\"Codigo\",opp.\"Linea\" ")


class DatabaseController():
    @classmethod
    def get_orders(cls):
        """
        Initialize database and execute query to retrieve active orders.
        Return cleaned data.
        """
        cursor = cls.init_db()
        data = cls.execute_query(cursor)
        return cls.clean_data(data)

    @classmethod
    def init_db(cls):
        """Initialize the connection to the database and return a cursor."""
        # establish connection
        conn = psycopg2.connect(
            database=DATABASE_NAME,
            user=USER_NAME,
            password=PASSWORD,
            host=HOST_NAME,
            port=PORT_NUMBER)
        # get cursors
        cur = conn.cursor()
        return cur

    @classmethod
    def execute_query(cls, cursor):
        """Execute query to retrieve active orders from database."""
        # run main first query
        cursor.execute(QUERY)
        return cursor.fetchall()

    @classmethod
    def clean_data(cls, data):
        """Clean given data. Return list OP numbers and cleaned data."""
        orders = []  # store all orders
        op_numbers = []  # store all OP numbers
        for row in data:
            # store op_number, client, description, machine, quantity, sheets
            order_dict = {}
            order_dict[VALUE_CLIENT] = row[INDEX_CLIENT]
            order_dict[VALUE_OP_NUMBER] = row[INDEX_OP_NUMBER]
            order_dict[VALUE_QUANTITY] = row[INDEX_QUANTITY]
            order_dict[VALUE_SHEETS] = row[INDEX_SHEETS]
            order_dict[VALUE_MACHINE] = row[INDEX_MACHINE]
            order_dict[VALUE_DESCRIPTION] = row[INDEX_DESCRIPTION]
            order_dict[VALUE_DUE_DATE] = row[INDEX_DUE_DATE]
            # store OP number
            op_numbers.append(row[INDEX_OP_NUMBER])
            processes = []  # store processes
            plastico = ""  # format process Plastico
            for index, item in enumerate(row):
                if item == 'X':
                    if index == INDEX_PLASTICO_T:
                        plastico = "Tiro"
                    elif index == INDEX_PLASTICO_TR:
                        plastico = "Tiro/Retiro"
                    elif (index == INDEX_PLASTICO_MATE or
                            index == INDEX_PLASTICO_BRILLANTE):
                        # add plastico
                        processes.append("{} {}".format(
                            INDICES[index][VAL_VALUE], plastico))
                    else:  # not plastico(s)
                        # add process
                        processes.append("{}".format(
                            INDICES[index][VAL_VALUE]))
            # store processes in dict
            order_dict[VALUE_PROCESSES] = processes
            # add dict to list of orders
            orders.append(order_dict)
        # return list of all info from given data
        return op_numbers, orders
