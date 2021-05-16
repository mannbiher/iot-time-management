import unittest

import mqtt_publish



class TestLeetCode(unittest.TestCase):
    def test_find_file(self):
        filenames = mqtt_publish.get_files_by_mdate('/var/tmp/pcap')
        print(filenames)

    


if __name__ == '__main__':
    # USERNAME = os.environ['USERNAME']
    # PASSWORD = os.environ['PASSWORD']
    # COOKIE = os.environ['COOKIE']

    unittest.main()
