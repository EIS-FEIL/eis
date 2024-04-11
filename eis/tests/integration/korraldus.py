# -*- coding: utf-8 -*-

from .integrationtestbase import *

toimumisaeg_id = 2940 # unit.test

class Korraldus(IntegrationTestBase):
    app_name = 'ekk'

    def _login(self):
        """Parooliga sisselogimine"""
        res = self.app.post('/login/signin',
            {
                'username': 'ADMIN',
                'parool': 'admin',
            }
        )
        assert res.status_int == 302

    def test_01_valjastus(self):
        self._login()

        url = '/korraldamine/%d/valjastus' % toimumisaeg_id
        # koguste arvutamine
        res = self.app.post(url,
                            {
                                'sub':'kogused',
                                'arvuta_kogused': 'Arvuta kogused',
                                'sailitakoodid': '1',
                            })
        #print url
        #print res.body
        assert res.status_int == 302

        # hindamiskirjete loomine
        res = self.app.post(url + '?sub=hindamisprotokollid&toimumisaeg_id=%s' % toimumisaeg_id)
        assert res.status_int == 302
        #print url
        #print res.body
        
        # ymbrike ja turvakottide loomine
        res = self.app.post(url + '?sub=ymbrikud&toimumisaeg_id=%s' % toimumisaeg_id)
        assert res.status_int == 302
        
        # kontroll
        res = self.app.get(url + '?op=kontrolli')
        #print url
        #print res.body
        self.assertEqual(res.status_int, 200)
        
