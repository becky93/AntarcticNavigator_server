import os
import shutil
import time
import modisProcessing.main_processing

import threading

class check_process(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval
        range_file = open('range.txt')
        self.cu_range = range_file.readline()
        range_file.close()

    def run(self):
        self.process()

    def process(self):
        while True:

            src = os.getcwd() + '/modisdownload/Data/Modis_data/'
            dst = os.getcwd() + '/modisProcessing/MODIS/hdf/'

            filelist = []

            for dirpath, dirnames, filenames in os.walk(src):
                for filename in filenames:
                    if filename.startswith('MOD') and filename.endswith('.hdf'):
                        filelist.append('.'.join(filename.split('.')[0:-1]))
            filelist.sort()
            print(filelist)

            range_file = open('range.txt')
            value = range_file.readline()
            range_file.close()
            print value
            values = value.split(' ')
            print(values)
            rightlon = float(values[1])
            leftlon = float(values[0])
            rightlat = float(values[3])
            leftlat = float(values[2])

            iscrop = True

             for filename in filelist:
                src_file = src + filename + ".hdf"
                dst_file = dst + filename + ".hdf"
                if os.path.exists(dst_file):
                    continue
                else:
                    from shutil import move
                    move(src_file, dst_file)
                    # os.rename(src_file, dst_file)

                    print('preprocess file "%s"......' % filename)
                    newname, iscrop = modisProcessing.main_processing.updateRaster(filename, leftlon, leftlat, rightlon, rightlat)

            zero_mark = False
            if len(filelist) != 0:
                # clear old files
                import clearfile
                clearfile.clear_raster()
                clearfile.clear_files()
            else:
                zero_mark = True

            # modis file update
            if (not zero_mark) or (self.cu_range != value):
                fileset = set()
                for dripath, dirnames, filenames in os.walk('modisProcessing/MODIS/tiff/arcmapWorkspace/'):
                    for filename in filenames:
                        if filename.split('.')[0].endswith('_crop'):
                            fileset.add(int(filename.split('.')[0].split('_')[0]))
                fileset = sorted(fileset, reverse=True)
                print fileset

                if fileset != []:
                    if zero_mark and value != self.cu_range:
                        newfilename = str(fileset[0]) + '_CURRENT_RASTER_1000'
                        from modisProcessing import RasterManagement
                        iscrop = RasterManagement.cropandmask(leftlon, leftlat, rightlon, rightlat, newfilename)

                    if iscrop:
                        if os.path.exists('test/'):
                            shutil.rmtree('test/')
                        os.mkdir('test/')
                        for dripath, dirnames, filenames in os.walk('modisProcessing/MODIS/tiff/arcmapWorkspace/'):
                            for filename in filenames:
                                if str(fileset[0]) == filename.split('.')[0].split('_')[0] and (not filename.endswith('.tif')) and 'crop' in filename:
                                    print filename
                                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + filename, 'test/' + filename)

                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.lonlat', 'test/' + newfilename + '.lonlat')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.prob', 'test/' + newfilename + '.prob')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.jpg', 'test/' + newfilename + '.jpg')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.cost', 'test/' + newfilename + '.cost')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.ice', 'test/' + newfilename + '.ice')

                        import sendemail
                        from mailutil import getemailpsw
                        email, psw = getemailpsw(2)
                        sendemail.send_file_zipped('test', ['PolarRecieveZip@lamda.nju.edu.cn'], psw, email)
            else:
                print 'no modis file updated'

            self.cu_range = value

            time.sleep(self.interval)

if __name__ == '__main__':
    process_interval = 300
    p = check_process(process_interval)
    p.start()


