# copa

**Copy Once, Paste Anywhere**

-----

## Client

### You can run copa client in two ways

- Download the compiled executable client from releases page **[recommended]**

[https://github.com/taojy123/copa/releases](https://github.com/taojy123/copa/releases)

In Mac, you should run client in command:
```
chmod a+x copa_mac
./copa_mac
```


- Or, run the source code script

```
git clone https://github.com/taojy123/copa
cd copa/client
pip install -r requirements.txt
python copa.py
```


### Configuration

`copaconf.json` will auto automatic generated while running

You can change it by text editor

```
{
  "host": "http://copa.tslow.cn",  // Server address, default is the public server
  "token": "test1",    // Clipboard will synchronize in the same token, please set your unique token 
  "interval": 5,       // Synchronization interval
  "language": "zh",    // Currently only support "en" and "zh", default is English
  "http_proxy": "",    // Your can set a http proxy if necessary
  "https_proxy": ""    // if https_proxy is blank, it will be the same with http_proxy
}
```


## Server

### You can contect to copa server in three ways

- Use the public server **[recommended]**

Just set host `http://copa.tslow.cn` in `copaconf.json`


- Or, deploy your own server by docker

```
git clone https://github.com/taojy123/copa
cd copa/server
docker build -t copa-server .
docker run -p 80:8000 -d copa-server
```

- Or, deploy your own server by run source code

```
git clone https://github.com/taojy123/copa
cd copa/server
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn -w 5 -b 0.0.0.0:80 copa.wsgi
```


