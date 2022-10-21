import os, queue, threading, time, random, pythoncom
from celery import Celery
from threading import Lock
from win32com.client import DispatchEx
from excel_crawler import ExcelCrawler
from excel_model import Session, Index, Table, Region, Dataset


celery = Celery(
        'celery_task',
        backend='rpc://',
        broker='pyamqp://'
    )

@celery.task()
def task_xls2pdf(filepath, table):
    if os.path.exists(filepath.split('.xls')[0]+'.pdf') == False:
        pythoncom.CoInitialize()
        ea = DispatchEx("Excel.Application")
        ea.Visible = False    
        ea.DisplayAlerts = 0   
        books = ea.Workbooks.Open(filepath,False)
        books.ExportAsFixedFormat(0, 'D:\\excel2mysql\\almanac_backend\\static\\'+table+'.pdf')
        books.Close(False)
        ea.Quit()
        pythoncom.CoUninitialize()

    return '/static/'+table+'.pdf'

@celery.task(bind=True)
def task_data_inject(self, json):
    Session()
    region = Session.query(Region).get(int(json['regionId']))
    excel_files = []
    for r, d, f in os.walk('.\\统计年鉴\\' + region.name):
        for file in f:
            if '.xls' in file:
                excel_files.append(os.path.join(r, file))
    total = len(excel_files)
    i = 0
    for file in excel_files:
        try:
            ec = ExcelCrawler(loc=file)
            htap = file[::-1].split('\\', 1)
            htap[0] = ('\\'+ec.table_name+'.xls')[::-1]
            path = ''.join(htap)[::-1]
            os.rename(file, path)
            table = Session.query(Table).filter(Table.name==ec.table_name).one_or_none()
            table = Table(name=ec.table_name)
            region.tables.append(table)
        except Exception as e:
            print(e)
        else:
            if '各' not in table.name:
                required_indexes = json['indexes']
                colnames_ = ec.colnames.copy()
                rownames_ = ec.rownames.copy()
                for ck, cv in colnames_.items():
                    if cv.isdigit():
                        continue
                    should_delete = True
                    for idx in required_indexes:
                        if idx in cv or cv in idx:
                            should_delete = False
                            break
                    if should_delete:
                        del ec.colnames[ck]
                for rk, rv in rownames_.items():
                    if rv.isdigit():
                        continue
                    should_delete = True
                    for idx in required_indexes:
                        if idx in rv or rv in idx:
                            should_delete = False
                            break
                    if should_delete:
                        del ec.rownames[rk]
            ris, cis = {}, {}
            for cx in list(ec.colnames):
                cn = ec.colnames[cx]
                db_cn = Session.query(Index).filter_by(name = cn).one_or_none()
                if db_cn is None:
                    db_cn = Index(name = cn)
                db_cn.tables.append(table)
                cis[cx[0]] = db_cn
            for rx in list(ec.rownames):
                rn = ec.rownames[rx]
                db_rn = Session.query(Index).filter_by(name = rn).one_or_none()
                if db_rn is None:
                    db_rn = Index(name = rn)
                db_rn.tables.append(table)
                ris[rx] = db_rn
            rxs, cxs = list(ris), list(cis)
            for cx in cxs:
                for rx in rxs:
                    if ec.tb.cell_type(rx, cx) == 2:
                        ds = Dataset(ec.tb.cell_value(rx,cx))
                        ds.col_index = cis[cx]
                        ds.row_index = ris[rx]
                        ds.table = table
            time.sleep(.5)
        finally:
            i += 1
            self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': f'已处理{ec.table_name}'})
    region.state = 1
    Session.commit()
    Session.remove()
    return {'current': 1, 'total': 1, 'status': 'success'}

# @celery.task(bind=True)
# def task_data_inject(self):
#     """Background task that runs a long function with progress reports."""
#     verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
#     adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
#     noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
#     message = ''
#     total = random.randint(10, 50)
#     for i in range(total):
#         if not message or random.random() < 0.25:
#             message = '{0} {1} {2}...'.format(random.choice(verb),
#                                               random.choice(adjective),
#                                               random.choice(noun))
#         self.update_state(state='PROGRESS',
#                           meta={'current': i, 'total': total,
#                                 'status': message})
#         time.sleep(1)
#     return {'current': 100, 'total': 100, 'status': 'Task completed!',
#             'result': 42}