import json
import sys
import os

def read_json(t_file):
  j_file = open(t_file).read()
  return json.loads(j_file)

def save_json(json_dict, save_name):
  with open(save_name, 'w') as outfile:
    json.dump(json_dict, outfile)  

def open_txt(t_file):
  os.system('pwd')
  f = open(t_file, 'r')
  txt_file = f.readlines()
  return [t.strip() for t in txt_file]
