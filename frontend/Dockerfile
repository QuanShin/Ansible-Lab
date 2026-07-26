FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN printf '%s\n' \
  'Built as part of Docker training' \
  > /image-build-info.txt

COPY index.html ./index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
