from pysnmp.entity.rfc3413.oneliner.ntforg import *

if version_info[:2] < (2, 6):
    def next(iter):
        return iter.next()

def sendNotification(snmpEngine, authData, transportTarget, contextData,
                     notifyType, varBinds, **options):
    """Creates a generator to send one or more SNMP notifications.

    On each iteration, new SNMP TRAP or INFORM notification is send
    (:RFC:`3413#section-3.3`). The iterator blocks waiting for 
    INFORM acknowlegement to arrive or error to occur.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.entity.engine.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.entity.rfc3413.oneliner.auth.CommunityData` or :py:class:`~pysnmp.entity.rfc3413.oneliner.auth.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.entity.rfc3413.oneliner.target.UdpTransportTarget` or :py:class:`~pysnmp.entity.rfc3413.oneliner.target.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.entity.rfc3413.oneliner.ctx.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    notifyType : str
        Indicates type of notification to be sent. Recognized literal
        values are *trap* or *inform*.

    varBinds: tuple
        Single :py:class:`~pysnmp.smi.rfc1902.NotificationType` class instance
        representing a minimum sequence of MIB variables required for
        particular notification type.
        Alternatively, a sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        objects could be passed instead. In the latter case it is up to
        the user to ensure proper Notification PDU contents.
    
    Other Parameters
    ----------------
    **options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : str
        True value indicates SNMP engine error.
    errorStatus : str
        Non-zero value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to *varBinds[errorIndex-1]
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Notes
    -----
    The `sendNotification` generator will be exhausted immidiately unless
    an instance of :py:class:`~pysnmp.smi.rfc1902.NotificationType` class
    or a sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` `varBinds`
    are send back into running generator (supported since Python 2.6).

    Examples
    --------
    >>> from pysnmp.entity.rfc3413.oneliner.ntforg import *
    >>> g = sendNotification(SnmpEngine(),
    ...                      CommunityData('public'),
    ...                      UdpTransportTarget(('demo.snmplabs.com', 162)),
    ...                      ContextData(),
    ...                      'trap',
    ...                      NotificationType(ObjectIdentity('IF-MIB', 'linkDown')))
    >>> next(g)
    (None, 0, 0, [])
    >>> 

    """
    def cbFun(snmpEngine, sendRequestHandle,
              errorIndication, errorStatus, errorIndex,
              varBinds, cbCtx):
        cbCtx['errorIndication'] = errorIndication
        cbCtx['errorStatus'] = errorStatus
        cbCtx['errorIndex'] = errorIndex
        cbCtx['varBinds'] = varBinds

    cbCtx = {}

    ntfOrg = AsyncNotificationOriginator()

    while True: 
        if varBinds:
            ntfOrg.sendNotification(
                snmpEngine,
                authData,
                transportTarget,
                contextData,
                notifyType,
                varBinds,
                cbInfo=(cbFun, cbCtx),
                lookupMib=options.get('lookupMib', True)
            )

            snmpEngine.transportDispatcher.runDispatcher()

            errorIndication = cbCtx.get('errorIndication')
            errorStatus = cbCtx.get('errorStatus')
            errorIndex = cbCtx.get('errorIndex')
            varBinds = cbCtx.get('varBinds', [])
        else:
            errorIndication = errorStatus = errorIndex = None
            varBinds = []

        varBinds = ( yield errorIndication, errorStatus, errorIndex, varBinds )

        if not varBinds:
            break