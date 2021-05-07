import sys
sys.path.append('../../utils/')
import re
from python_utils import *
import argparse
import glob
import pdb
import pickle as pkl

sentence_split_regex = re.compile(r'(\W+)')

def open_txt(t_file):
  os.system('pwd')
  f = open(t_file, 'r')
  txt_file = f.readlines()
  return [t.strip() for t in txt_file]

def read_json(t_file):
  j_file = open(t_file).read()
  return json.loads(j_file)

def save_json(json_dict, save_name):
  with open(save_name, 'w') as outfile:
    json.dump(json_dict, outfile)  


def split_sentence(sentence):
    sentence = [s.lower() for s in sentence_split_regex.split(sentence.strip()) if len(s.strip()) > 0]
    if sentence[-1] != '.':
        return sentence
    return sentence[:-1]

def captions_preprocess(raw_descriptions):
  #takes raw descriptions (*.tsv) and generates json file in the same format as MSCOCO  
  json_descriptions = {}
  json_descriptions['images'] = []
  json_descriptions['annotations'] = []
  json_descriptions['type'] = 'captions'

  des = open_txt(raw_descriptions)
  # Chandra
  #des = [d.split('\t') for d in des] 
  des = [d for d in des] 
  #important_info = [(d[-1], d[-2]) for d in des if d[-7] == '']

  descriptions = des
  #descriptions = zip(*important_info)[0]
  des = open_txt(dataset_hash[args.description_type]['image_names'])

  #im_ids = ['/'.join(i.split('/')[-2:]) for i in zip(*important_info)[1]]
  im_ids = [d for d in des]

  unique_ims = list(set(im_ids))

  for unique_im in unique_ims:
    im = {}
    im['file_name'] = unique_im
    im['id'] = unique_im
    json_descriptions['images'].append(im)

  count = 0
  for description, im_id in zip(descriptions, im_ids):
    a = {}
    a['caption'] = description
    a['id'] = count
    a['image_id'] = im_id
    count += 1 
    json_descriptions['annotations'].append(a)

  return json_descriptions

def create_json(im_to_annotations, im_to_images, set_ims):
  json_descriptions = {}
  json_descriptions['images'] = []
  json_descriptions['annotations'] = []
  json_descriptions['type'] = 'captions'

  for im in set_ims:
    # Chandra
    try:
      json_descriptions['images'].append(im_to_images[im])
      json_descriptions['annotations'].extend(im_to_annotations[im])
    except KeyError:
	  pass
  
  return json_descriptions

def create_finegrained(im_to_annotations, im_to_images, ims):

  ims = open_txt(ims)

  descriptions = create_json(im_to_annotations, im_to_images, ims)
  
  return descriptions 

def create_json_finegrained(im_to_annotations, im_to_images, image_base_path, train_ims, test_ims):

  train_classes = open_txt(train_ims)
  test_classes = open_txt(test_ims)

  train_descriptions = create_json(train_ims)
  if test_ims: 
    test_descriptions = create_json(test_imso)
  else:
    test_descriptions = None
  
  return train_descriptions, test_descriptions 

def create_im_dicts(descriptions):
  im_to_annotations = {}
  for anno in descriptions['annotations']:
    if anno['image_id'] in im_to_annotations.keys():
      im_to_annotations[anno['image_id']].append(anno)
    else:
      if not 'cub_missing' in anno['image_id']:
        im_to_annotations[anno['image_id']] = [anno]

  im_to_images = {}
  for im in descriptions['images']:
    im_to_images[im['id']] = im

  return im_to_annotations, im_to_images

def save_descriptions(save_dict, save_tag):
  save_path = 'descriptions.json'
  save_json(save_dict, save_path) 
  print 'Saved captions to %s.\n' %save_path 
  print "WROTE JSON FILE IN CURRENT DIRECTORY\n"

dataset_hash = {'numbers': {'raw_descriptions': 'digitcaptions.txt', 
                         'preprocessor': captions_preprocess,
			 'image_names': 'number_images.txt'},

 		'flights': {'raw_descriptions': 'test_caption_new.txt', 
                         'preprocessor': captions_preprocess,
			 'image_names': 'test_image_new.txt'}}

if __name__ == '__main__':

  parser = argparse.ArgumentParser()

  parser.add_argument("--description_type", type=str, default='flights')
  parser.add_argument("--splits", type=str, default=None)
  parser.add_argument("--generate", type=str, default='gen_json')

  args = parser.parse_args()
  print args
  		
  if "gen_json" == args.generate:
  	raw_descriptions = dataset_hash[args.description_type]['raw_descriptions']
  	json_descriptions = dataset_hash[args.description_type]['preprocessor'](raw_descriptions)

        save_tag = args.description_type
	save_descriptions(json_descriptions, save_tag)
  	#im_to_annotations, im_to_images = create_im_dicts(json_descriptions)

  	#print "\nImage Annotations", im_to_annotations
  	#print "\nImage names", im_to_images
	ims = args.splits.split(',')
   	if 'train' in ims: #make vocab from train set
		vocab_file = open('vocab.txt', 'w')
	      	words = [] 
		for caption in json_descriptions['annotations']:
			words.extend([s.strip() for s in split_sentence(caption['caption'])])
			vocab = sorted(list(set(words)))
		for v in vocab:
			vocab_file.writelines('%s\n' %v)
		vocab_file.close()

	print "WROTE VOCAB.TXT IN CURRENT DIRECTORY\n"
  if "preds" == args.generate:
  	feature_probs = pkl.load(open('digit_feature_8192.p', 'r'))
  	f = open('number_images.txt', 'r')
  	txt_file = f.readlines()
  	file_names = [t.strip() for t in txt_file]

  	digit_feature_probs = dict(zip(file_names, feature_probs))

  	print digit_feature_probs
  	pkl.dump(digit_feature_probs, open('digit_features_probs.p', 'w'))
	  
  	print "Digit feature probabilities."
