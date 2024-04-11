# teavituskalendri asemel on andmekogu "notifications",
# vt https://www.riha.ee/Infos%C3%BCsteemid/Vaata/70006317-notifications

from datetime import datetime, date, timedelta
from eis.lib.xtee.xroad import *
import logging
log = logging.getLogger(__name__)

import eiscore.const as const

class Notifications(XroadClientEIS):
    "Eesti.ee teavituskalendri teenuste kasutamine"
    producer = 'notifications'
    namespace = 'http://notifications.eesti.ee'
    
    # teavituskalendris registreeritud syndmuste liikide nimetused,
    # kasutusel identifikaatoritena
    LIIK_RE = 141 # Riigieksami teavitus
    LIIK_TE = 142 # Kodakondsuseksami teavitus
    LIIK_SE = 144 # Keele tasemeeksami teavitus
    LIIGID = {const.TESTILIIK_RIIGIEKSAM: LIIK_RE,
              const.TESTILIIK_TASE: LIIK_TE,
              const.TESTILIIK_SEADUS: LIIK_SE,
              }

    def createEvent(self, testiliik, kirjeldus, kuupaev, lugejad, event_id):
        "Sündmuse lisamine teavituskalendrisse"
        if testiliik == const.TESTILIIK_RV:
            testiliik = const.TESTILIIK_RIIGIEKSAM
        subscriptionId = self.LIIGID.get(testiliik)
        if not subscriptionId:
            return 'Seda testiliiki teavitusteenuses ei kasutata', None
        #event_id = None
        event = E.event(E.subsciptionId(subscriptionId))
        if event_id:
            # olemasoleva syndmuse muutmisel
            event.append(E.eventId(event_id))
        event.append(E.name('Eksami teavitus', lang='et'))
        event.append(E.description(kirjeldus, lang='et'))
        event.append(E.eventTime(kuupaev))
        # teavitusteenuse vea tõttu on vaja avaldamise aeg näidata 3 tundi tegelikust varasem
        dpub = datetime.now() - timedelta(hours=3)
        event.append(E.publishTime(dpub))
        event.append(E.sendToAllSubscribers(False))
        if not event_id:
            # uue syndmuse lisamisel lisame saajad
            recipients = E.addRecipients()
            for isikukood in lugejad:
                recipients.append(E.code(isikukood))
            event.append(recipients)
        request = E.parameters(event)
        
        list_path = ['/eventResponses/eventResponse']
        try:
            res = self.call('createOrUpdateEvent', request, list_path)
            if res:
                status = res.status
                if status.statusCode != '0':
                    return None, status.statusMessage                
                responses = res.eventResponses
                if responses:
                    for response in responses.eventResponse:
                        # status,eventId,failedRecipients,addedRecipients,removedRecipients
                        e_status = response.status
                        if e_status.statusCode != '0':
                            return None, e_status.statusMessage
                        try:
                            eventId = int(response.eventId)
                        except:
                            eventId = None
                return None, eventId
        except SoapFault as e:
            return e.faultstring, None
        return None, None

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()
    from eis.scripts.scriptuser import *
    userId = None
    reg = Notifications(settings=registry.settings, userId=userId)
    try:
        print(reg.allowedMethods())
        #print(reg.listMethods())
    except SoapFault as e:
        print(e.faultstring)
        raise

    if True:
        ik = named_args.get('ik')
        print('ik=%s' % ik)
        if ik and len(ik) == 11:
            lugejad = [ik]
            err, event_id = reg.createEvent(const.TESTILIIK_RIIGIEKSAM, 'Testsündmus', date.today(), lugejad, None)
            print('err=%s, event_id=%s' % (err, event_id))
        
