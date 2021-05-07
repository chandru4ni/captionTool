import os
import sys
import numpy as np
import cv2
import random
import argparse

BOX_WIDTH=25
BOX_HEIGHT=25
maxdimensions = {}

DIM1 = 150
DIM2 = 150
def draw_hmBoxes(rawhmfilename):
	global BOX_WIDTH, BOX_HEIGHT, maxdimensions
	rawhm_file = open(rawhmfilename, 'r')
	rawhm_lines = rawhm_file.readlines()
	rawhm_lines = rawhm_lines[2:]
	tmp = DIM1*DIM2
	rawhm = np.zeros((3,tmp), dtype=np.float64)
	for i in range(DIM1):
		temp0 = np.zeros(DIM1, dtype=np.float64)
		temp0 = rawhm_lines[i].split('\n')[0].split(' ')
		temp0 = [float(ele) for ele in temp0[:DIM1]]
		temp1 = np.zeros(DIM1, dtype=np.float64)
		temp1 = rawhm_lines[i+DIM1].split('\n')[0].split(' ')
		temp1 = [float(ele) for ele in temp1[:DIM1]]
		temp2 = np.zeros(DIM1, dtype=np.float64)
		temp2 = rawhm_lines[DIM1+DIM2+i].split('\n')[0].split(' ')
		temp2 = [float(ele) for ele in temp2[:DIM1]]

		rawhm[0][(i*DIM1):(i+1)*DIM1] = temp0[:]
		rawhm[1][(i*DIM1):(i+1)*DIM1] = temp1[:]
		rawhm[2][(i*DIM1):(i+1)*DIM1] = temp2[:]

	prevmaxabs = 0
	height = 0
	width = 0
	unsorted_vs = np.zeros(DIM1*DIM1, dtype=np.float64)
	for i in range(DIM1*DIM1):
		unsorted_vs[i] = float(rawhm[0][i] + rawhm[1][i] + rawhm[2][i]) / 3.0

	vs = -np.sort(-unsorted_vs) # sorted in descending order
	boxIdx = 0
	for sorted_idx in range(DIM1*DIM1):
		maxabs = vs[sorted_idx]
		maxIndex = list(unsorted_vs).index(maxabs)
		maxheight = maxIndex%DIM1
		maxwidth = int(maxIndex/DIM1)
		#print maxabs, maxIndex, maxheight, maxwidth

		break_flag = False
		for boxindex, maxdims in maxdimensions.iteritems():
			break_flag = False
			for w in range(maxdims[1]-BOX_WIDTH, maxdims[1]+BOX_WIDTH):
				for h in range(maxdims[0]-BOX_HEIGHT, maxdims[0]+BOX_HEIGHT):
					new_i = (h) + (w) * DIM1
					if maxIndex == new_i:
						break_flag = True
						break
				if break_flag == True:
					break
			if break_flag == True:
				break
		if break_flag == True:
			continue

		maxdimensions.update({boxIdx:[maxheight, maxwidth, maxIndex]})
		#print maxdimensions
		boxIdx = boxIdx+1

		if boxIdx == 4:
			break


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	#parser.add_argument("--imgname", type=str, default=None)
	parser.add_argument("--hmname", type=str, default=None)
	parser.add_argument("--rawhmname", type=str, default=None)

	args = parser.parse_args()

	draw_hmBoxes(args.rawhmname)

	#img = cv2.imread(args.imgname, cv2.IMREAD_COLOR)
	hmimg = cv2.imread(args.hmname, cv2.IMREAD_COLOR)

	for boxIdx, maxdims in maxdimensions.iteritems():
		r = random.randrange(0, 255, 1)
		g = random.randrange(0, 255, 1)
		b = random.randrange(0, 255, 1)
		hmimg = cv2.rectangle(hmimg, (maxdims[0]+BOX_HEIGHT,maxdims[1]-BOX_WIDTH), \
			(maxdims[0]-BOX_HEIGHT,maxdims[1]+BOX_WIDTH), (r, g, b), 1)

	cv2.imwrite("hmImageBoxes.png", hmimg)
