

# また、途中できあがるeggs.csvを保存しておくと一度取得した全データの保存が効く。
# すべてのコードについて保存先を指定することができ、
# PROJECT_NAMEで指定するフォルダに格納されるように構成している。
# from google.colab import drive
# drive.mount('/content/drive')
# PROJECT_NAME = 'EDINETScraping'
# BASE_DIR = f'/content/drive/My Drive/Colab Notebooks/data/{ PROJECT_NAME }/'

# データをストックする起点フォルダを作成
PROJECT_NAME = 'EDINETScraping'
BASE_DIR = f'/Users/bonnychan/PycharmProjects/sd/{ PROJECT_NAME }/'

import os
os.makedirs( BASE_DIR ,exist_ok=True )

# ＜＜＜＜＜＜＜＜　ここから　＞＞＞＞＞＞＞＞＞＞

# EDINETのAPIから必要なXBRLファイルのURLを取得し、dat_download.csvというURL一覧のファイルを作成する。
# 以下のCell-2 Cell-3をそのまま実行するとdat_download_200601_200602.csvというファイルが作成される。

# GoogleColab:Cell-2
import csv ,time ,re ,os ,json ,requests
from tqdm import tqdm
from datetime import datetime ,timedelta

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# catcher クラスを作成
# catcher を初期化して値を設定する
# os.getcwd 「Pythonが実行されている作業ディレクトリ（カレントディレクトリ）の絶対パスを文字列として返す」
class catcher():
    def __init__(self, since, until, base_dir=None, wait_time=2):
        self.csv_tag = ['id', 'title', 'url', 'code', 'update']
        self.encode_type = 'utf-8'
        self.wait_time = wait_time
        self.base_url = 'https://disclosure.edinet-fsa.go.jp/api/v1/documents'
        self.out_of_since = False
        self.since = since
        self.until = until
        self.file_info_str = since.strftime('_%y%m%d_') + until.strftime('%y%m%d')
        self.file_name = f'dat_download{ self.file_info_str }.csv'
        self.base_path = f'{ os.getcwd() if base_dir == None else base_dir }'

# 特殊メソッド「__get_link_info_str」を作成
    def __get_link_info_str(self, datetime):
        str_datetime = datetime.strftime('%Y-%m-%d')
        params = {"date": str_datetime, "type": 2}
# APIからJason形式でリクエストGET。
        count, retry = 0, 3
        while True:
            try:
                response = requests.get(f'{ self.base_url }.json', params=params, verify=False)
                return response.text
            except Exception:
                print(f'{str_datetime} のアクセスに失敗しました。[ {count} ]')
                if count < retry:
                    count += 1
                    time.sleep(3)
                    continue
                else: raise

    def __parse_json(self, string):
        res_dict = json.loads( string )
        return res_dict["results"]

    def __get_link( self ,target_list ) :
        edinet_dict = {}
        for target_dict in target_list :
            title = f'{ target_dict["filerName"] } { target_dict["docDescription"] }'
            if not self.__is_yuho( title ) : continue
            docID = target_dict["docID"]
            url = f'{ self.base_url }/{ docID }'
            edinet_code = target_dict['edinetCode']
            updated = target_dict['submitDateTime']
            edinet_dict[ docID ] = { 'id':docID ,'title':title ,'url':url ,'code':edinet_code ,'update':updated }
        return edinet_dict

    def __is_yuho( self ,title ) :
        if all( ( s in str( title ) ) for s in [ '有価証券報告書' ,'株式会社' ] ) and '受益証券' not in str( title ) :
            return True
        return False

    def __dump_file( self ,result_dict ) :
        with open( os.path.join( self.base_path ,self.file_name ) ,'w' ,encoding=self.encode_type ) as of :
            writer = csv.DictWriter( of ,self.csv_tag ,lineterminator='\n' )
            writer.writeheader()
            for key in result_dict : writer.writerow( result_dict[ key ] )

    def create_xbrl_url_csv( self ) :
        print( f'since: { self.since.strftime( "%Y-%m-%d" ) } ,until: { self.until.strftime( "%Y-%m-%d" ) } ({ self.file_info_str })' )
        target_date ,result_dict = self.since ,{}
        while True :
            print( f'date { target_date.strftime( "%Y-%m-%d" ) }, loading...' )
            response_string = self.__get_link_info_str( target_date )
            target_list = self.__parse_json( response_string )
            info_dict = self.__get_link( target_list )
            result_dict.update( info_dict )
            time.sleep( self.wait_time )
            target_date = target_date + timedelta( days=1 )
            if target_date > self.until : break
        self.__dump_file( result_dict )
        print( 'complete a download!!' )

def edinet_operator( since ,until ,base_dir=None ):
    edinet_catcher = catcher( since ,until ,base_dir )
    edinet_catcher.create_xbrl_url_csv()

#GoogleColab:Cell-3
from datetime import datetime

since = datetime.strptime('2020-06-01' ,'%Y-%m-%d')
until = datetime.strptime('2020-06-02' ,'%Y-%m-%d')
edinet_operator(since, until, base_dir = BASE_DIR)

#pip install python-xbrl


