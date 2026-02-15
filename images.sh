cd bing-wallpaper-compressed
for file in *.webp; do
  convert "$file" "${file%.webp}.jpg"
done
