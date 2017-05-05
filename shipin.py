__author__ = 'minfon'
# -*- coding: utf-8 -*-
import urllib2
from sgmllib import SGMLParser
import MySQLdb

i = 0
s1 = 0
s2 = 0

class LrcHTMLParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)

        #self.is_imgsrc = ""
        self.entry = []
        #div_tag_unclosed = ''
        self.div_tag_unclosed = ''
        self.p_tag_unclosed = ''
        self.br_tag_unclosed = ''
        #self.p_tag_unclosed = ''
        #sub=''
        #self.dat = ['','','','']
        #self.dat_2d  = ['','','','']
        self.datas = []
        self.content = []


    def start_div(self,attrs):
        for name,value in attrs:
            if name =='class' and value == 'video_con1_text_top':
                self.div_tag_unclosed = 'video_con1_text_top'
            if name =='style' and value == 'display:none':
                self.div_tag_unclosed = 'display:none'

    def start_p(self,attrs):
        self.p_tag_unclosed = 1

    def end_p(self):
        self.p_tag_unclosed = ''

    def end_div(self):
        pass
        #if self.div_tag_unclosed == 'video_con1_text' :
         #   self.div_tag_unclosed =''
            #self.entry.append(self.datas.pop().strip())
            #self.contents =  self.datas.pop().strip()

    def start_br(self,attrs):
        self.br_tag_unclosed = 1

    def end_br(self):
        self.br_tag_unclosed = ''

    #def handle_data(self, data):
    #    if ( self.div_tag_unclosed  == 1 and self.p_tag_unclosed  == 1 ):
    #        self.entry.append(data)
    def handle_data(self, data):
        #if ( self.div_tag_unclosed  == 'video_con1_text_top' and self.p_tag_unclosed  == 1 ):
         #   self.entry.append(data)
        if ( self.div_tag_unclosed  == 'display:none' and self.p_tag_unclosed  == 1 ):
           self.entry.append(data)
        if self.div_tag_unclosed == 'display:none' and self.br_tag_unclosed == 1:
           self.div_tag_unclosed =''
        #if self.div_tag_unclosed == 'video_con1_text_top' and self.br_tag_unclosed == 1:
        #   self.div_tag_unclosed =''
    #        print 'data',data
        #self.datas.append(data)

class MyHTMLParser(SGMLParser):

 def __init__(self):
        SGMLParser.__init__(self)

        self.is_imgsrc = ""
        self.entry = []
        div_tag_unclosed = ''
        self.li_tag_unclosed = ''
        self.p_tag_unclosed = ''
        sub=''
        self.dat = ['','','','','']
        self.dat_2d  = ['','','','','']
        self.lrc = ""

 def start_li(self,attrs):
     self.li_tag_unclosed = 1

 def start_img(self, attrs):
     for name,value in attrs:
         if ( name=='data-original' and self.li_tag_unclosed == 1):
             sub = value[:4]
             if ( sub == 'http'):
                self.entry.append(value)
                self.dat[0]= value
             else:
                self.entry.append('http://www.chinanews.com'+value)
                self.dat[0]= 'http://www.chinanews.com'+value


         elif ( name=='src' and self.li_tag_unclosed == 1 ):
             sub = value[:4]
             if ( sub == 'http'):
                 self.entry.append(value)
                 self.dat[0]= value
             else:
                 self.entry.append('http://www.chinanews.com'+value)
                 self.dat[0]= 'http://www.chinanews.com'+value

 def end_img(self):
      pass

 def start_p(self, attrs):
     self.p_tag_unclosed = 1

 def start_a(self, attrs):
     for name,value in attrs:
         if ( name=='href' and self.p_tag_unclosed == 1 and self.li_tag_unclosed == 1):
             sub = value[:4]
             if ( sub == 'http'):
                 self.entry.append(value)
                 self.dat[1]=value
             else:
                 self.entry.append('http://www.chinanews.com'+value)
                 self.dat[1]='http://www.chinanews.com'+value

 def end_a(self):
     pass

 def end_p(self):
     self.p_tag_unclosed = ''

 def end_li(self):
     self.li_tag_unclosed = ''


 def handle_data(self, data):
     if (self.p_tag_unclosed  == 1 and self.li_tag_unclosed == 1 ):
        self.entry.append(data)
        self.dat[2]=data
        print self.dat[1]
        if( self.dat[1] ):
         sf = urllib2.urlopen(self.dat[1])
         if( sf ):
           c = sf.read()
           s1 = c.find('vInfo=')
           s2 = c.find('%26')
           if( s1 > 0 and s2-s1 <300 ):
               d = c[s1+6 : s2].split('"')[0]
             #print c[s1+6 : s2]
             # self.dat[3] = c[s1+6:s2]
               self.dat[3] = d
               print d
           sf.close()
         cont1 = urllib2.urlopen(self.dat[1]).read()
         lrc = LrcHTMLParser()
         lrc.feed(cont1)
         for item in lrc.entry:
            #print (item.decode('gbk').encode('utf8'))
            self.lrc = self.lrc + item +"\r\n"
         self.dat[4] = self.lrc
         print self.lrc.decode('gbk').encode('utf8')
        if(self.dat[0] !='' and self.dat[1] !='' and self.dat[2] !=''):
            #self.dat_2d.append(self.dat)
            cursor = db.cursor()
            para = (self.dat[2].decode('gbk').encode('utf8'),self.dat[0],self.dat[1],self.dat[3],self.dat[4].decode('gbk').encode('utf8'))
            cursor.execute(query,para)    #write to MySQL database
            db.commit()
            self.dat = ['','','','','']
            self.lrc = ""



# connect to MYQL
db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="test",charset='utf8')
query = "insert IGNORE into chinanews(subject,imagelink,hyperlink,videolink,lrctext) values(%s , %s, %s, %s, %s)"


content = urllib2.urlopen('http://www.chinanews.com/shipin/').read()
listname = MyHTMLParser()
listname.feed(content)


#print all the entries
#for item in listname.entry:
#    print (item[i:].decode('gbk').encode('utf8'))



i=0

'''
for i in range(len(listname.dat_2d)-5):
    print i
    print(listname.dat_2d[i+5][0])  # imglink
    print(listname.dat_2d[i+5][1])  # hyperlink
    print(listname.dat_2d[i+5][2].decode('gbk').encode('utf8'))  #subject (UTF-8)
    print(listname.dat_2d[i+5][3])  #videoink
    print(listname.dat_2d[i+5][4].decode('gbk').encode('utf8'))  #lrctext (UTF-8)
    print '\n'
    cursor = db.cursor()
    para = (listname.dat_2d[i+5][2].decode('gbk').encode('utf8'),listname.dat_2d[i+5][0],listname.dat_2d[i+5][1],listname.dat_2d[i+5][3],listname.dat_2d[i+5][4].decode('gbk').encode('utf8'))
    i = i + 1
    cursor.execute(query,para)    #write to MySQL database

# execute  SQL command
#cursor.execute("SELECT * FROM chinanews")
#result = cursor.fetchall()

# output result
#for record in result:
#    print record[0],record[1],record[2],record[3]

db.commit()
'''

db.close()
