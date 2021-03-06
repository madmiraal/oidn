#!/usr/bin/env python

## Copyright 2018-2020 Intel Corporation
## SPDX-License-Identifier: Apache-2.0

import os
from collections import defaultdict
import argparse
import OpenImageIO as oiio

from config import *

def main():
  # Parse the command-line arguments
  cfg = parse_args(description='Splits a multi-channel EXR image into multiple feature images.')

  # Load the input image
  name, ext = os.path.splitext(cfg.input)
  if ext.lower() != '.exr':
    error('image must be EXR')
  image = oiio.ImageBuf(cfg.input)
  if image.has_error:
    error('could not load image')

  # Get the channels and group them by layer
  channels = image.spec().channelnames
  layer_channels = defaultdict(set)
  for channel in channels:
    if len(channel.split('.')) >= 3:
      layer, ch = channel.split('.', 1)
      layer_channels[layer].add(ch)
    else:
      layer_channels[None].add(channel)

  # Set default layer
  if not cfg.layer and len(layer_channels) == 1:
    cfg.layer = list(layer_channels.keys())[0]

  # Extract features
  FEATURES = {
    'hdr' : [
              ('R', 'G', 'B'),
              ('Noisy Image.R', 'Noisy Image.G', 'Noisy Image.B')
            ],
    'alb' : [
              ('albedo.R', 'albedo.G', 'albedo.B'),
              ('Denoising Albedo.R', 'Denoising Albedo.G', 'Denoising Albedo.B')
            ],
    'nrm' : [
              ('normal.R', 'normal.G', 'normal.B'),
              ('N.R', 'N.G', 'N.B'),
              ('Denoising Normal.X', 'Denoising Normal.Y', 'Denoising Normal.Z')
            ]
  }

  for feature, feature_channel_lists in FEATURES.items():
    for feature_channels in feature_channel_lists:
      # Check whether the feature is present in the selected layer of the image
      if cfg.layer:
        feature_channels = tuple([cfg.layer + '.' + f for f in feature_channels])
      if set(feature_channels).issubset(channels):
        # Save the feature image
        feature_filename = name + '.' + feature + ext
        print(feature_filename)
        new_channels = ('R', 'G', 'B') if len(feature_channels) == 3 else ('Y')
        feature_image = oiio.ImageBufAlgo.channels(image, feature_channels, new_channels)
        feature_image.write(feature_filename)
        break

if __name__ == '__main__':
  main()