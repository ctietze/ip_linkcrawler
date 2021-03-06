import httplib
import sys

class Iprods_Http_Utils:

    '''
    close connection to host
    '''
    def close(self):
        if self.connection is not None:
            self.connection.close()

    '''
    establish connection to host
    '''
    def connect(self):
        if self.connection is None:
            self.connection  = httplib.HTTPConnection(self.reportApp.DOMAIN)

        '''
    getResponseData
    '''
    def getResponseData(self, path):
        resLocation = ''
        resStatus = ''
        resReason = ''
        responseData = ''
        #if self.TIMEOUT:
        #    time.sleep(self.TIMEOUT)

        response = self.getResponse (path)

        if len(response) > 2:
            resLocation = response[0]
            resStatus   = response[1]
            resReason   = response[2]

            # save path or modified location
            if resLocation != path:
                self.reportApp.appendIntern(resLocation)
            self.reportApp.appendIntern(path)

            if resStatus >= 200 and resStatus < 300:
                responseData = response[3]
            else:
                #self.failedIntern.append(path)
                self.log.error("getData. Statuscode not in range [resLocation: %s, resStatus: %s, resReason: %s]. Skipped." % (resLocation, resStatus, resReason))

        else:
            #self.failedIntern.append(path)
            self.log.error("getData. Response Error [response: %s]. Skipped." % (response))
        # FI resStatus >= 200 and resStatus < 300:

        return responseData

    '''
    get a tuple of response values
    '''
    def getResponse(self, path):
        #self.log.debug(">>> getResponse [ path: %s]" % ( path))
        status = ''
        res = []

        headers = {"Connection": "keep-alive", "User-Agent": self.reportApp.USERAGENT}
        #if self.cookie is not None:
        #    headers['Cookie'] = self.cookie

        try:
            self.connect()
            #self.log.info(">>> getResponse [ path: %s, headers: %s]" % ( path, headers))
            self.connection.request('GET', path, None, headers=headers)
            response    = self.connection.getresponse()
            res = (path, response.status, response.reason, response.read())
            status = res[1]
            #print("[DOMAIN: %s, path: %s, status: %s]" % (self.DOMAIN, path, res[1]))
            #if self.cookie is None:
            #    self.cookie = response.getheader('set-cookie')

            #WebReportApp.log.debug("[cookie: %s, status: %s, path: %s]" % (self.cookie , status, path))
            # perform redirect to get page
            if status == 301 or status == 302:
                path = response.getheader("location")
                res = self.getResponse(path)
        except :
            self.close()
            exctype, value = sys.exc_info()[:2]
            self.log.exception("getResponse failed. path: %s, value: %s]"  %  (path, value))

        self.log.debug("<<< getResponse [status: %s]", status)
        return res

    '''
    check if statuscode is in the range of the config http status codes
    e.g. 404 in the range between 400 and 499
    '''
    @classmethod
    def isCodeInCodeRange(self, codes, code):
        result = False

        if code != '' :
            for level in codes.split(','):
                diff = -1
                try:
                    diff = int(code) - int(level)
                except ValueError:
                    exctype, value = sys.exc_info()[:2]
                    raise Exception("isCodeInCodeRange failed. exctype: %s, value: %s [code: %s, level: %s, diff %s]"  %  (exctype, value, code, level, diff))


                if diff > -1 and diff < 100:
                    result = True
                    break

        return result
