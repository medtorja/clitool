import boto3
import unittest
import clitool
import json

TESTSTACKNAME = "TEST-STACK"

class Tesstclitool(unittest.TestCase):

    def test1_create_stack(self):
        print("++++++++++++++++++++++++++++++++++++++++++")
        print(" test create stack from create_test.json  ")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print()
        with open("./create_test.json") as json_file:
            data = []
            try:
                data = json.load(json_file)
            except ValueError as e:
                print ('invalid json: %s' % e)
        clitool.create_stack(data, TESTSTACKNAME)
        print()
 
    
    def test2_list_stack(self):
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("            test list stack               ")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print()
        clitool.list_stack(TESTSTACKNAME)
        print()

 
    def test3_update_stack(self):
        print("++++++++++++++++++++++++++++++++++++++++++")
        print(" test update stack with update_test.json  ")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print()
        with open("./update_test.json") as json_file:
            data = []
            try:
                data = json.load(json_file)
            except ValueError as e:
                print ('invalid json: %s' % e)
        clitool.update_stack(data, TESTSTACKNAME)
        print()
 
    def test4_list_instances_updated(self):
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("        test list stack updated           ")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print()
        clitool.list_stack(TESTSTACKNAME)
        print()
 
    def test5_delete_instances(self):
        print("++++++++++++++++++++++++++++++++++++++++++")
        print("            test delete stack             ")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print()
        clitool.delete_stack(TESTSTACKNAME)
        print()

if __name__ == '__main__':
    unittest.main(warnings='ignore')
