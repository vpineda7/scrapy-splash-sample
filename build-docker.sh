docker build -t scrapy -f Dockerfile .
docker run --name scrapy_app -v $(pwd)/data_code:/code \
        --link splash_app:splash \
        -t -i -d \
        -p 8000:8000 -p 3000:3000\
        scrapy
