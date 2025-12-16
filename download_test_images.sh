#!/bin/bash
# MUSE Test Images Download Script
# These are all FREE Unsplash images (no attribution required)

mkdir -p test_images
cd test_images

echo "Downloading test images from Unsplash..."

# Living Room - gray sectional sofa with coffee table
echo "1/7 Living room..."
curl -L "https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=1920" -o living_room.jpg

# Kitchen - modern white kitchen with island
echo "2/7 Kitchen..."
curl -L "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1920" -o kitchen.jpg

# Dining Room - table with chairs
echo "3/7 Dining room..."
curl -L "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=1920" -o dining_room.jpg

# Marble texture - white with gray veining
echo "4/7 Marble sample..."
curl -L "https://images.unsplash.com/photo-1694176986566-b25cec213e91?w=1920" -o marble_sample.jpg

# Fabric texture - neutral woven
echo "5/7 Fabric sample..."
curl -L "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1920" -o fabric_sample.jpg

# Japandi/minimal style reference
echo "6/7 Japandi reference..."
curl -L "https://images.unsplash.com/photo-1725796608933-d4e809e5b370?w=1920" -o japandi_reference.jpg

# Designer chair (mid-century style)
echo "7/7 Chair reference..."
curl -L "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=1920" -o chair_reference.jpg

echo ""
echo "Done! Downloaded images:"
ls -la *.jpg

echo ""
echo "Ready for MUSE testing!"
