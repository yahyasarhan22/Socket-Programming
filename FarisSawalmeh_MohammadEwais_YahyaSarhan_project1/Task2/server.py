from socket import *
import os

host='127.0.0.1'
serverPort = 9903



def ErrorMessage(IP, PortNumber,connectionSocket):
    
    ResponseSender(404,'text/html',connectionSocket)
        
    ErrorMessageOnWebPage=(
        '<!DOCTYPE html>'
        '<html lang="en">'
        '<head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>Error 404</title>'
        '</head>'
        '<body>'
        '<h1 style = "text-align: center; color: red;">The file is not found</h1>'
        '<p style = "text-align: center; color: darkgray;"> IP Address: '+ str(IP)+' Port Number: '+str(PortNumber)+'</p>'
    )
    connectionSocket.send(ErrorMessageOnWebPage.encode())
    

def ResponseSender(StatusCode,File,connectionSocket):
    if StatusCode == 200:
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
    elif StatusCode == 404:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
    elif StatusCode == 307:
        connectionSocket.send("HTTP/1.1 307 Temporary Redirect\r\n".encode())
    
    if File.startswith('/text'):
        RespondWith=f"Content-Type: {File}; charset=utf-8\r\n"
    else:
        RespondWith=f"Content-Type: {File}\r\n"

    connectionSocket.send(RespondWith.encode())
    connectionSocket.send("\r\n".encode())

    if StatusCode == 200:
        print(f"HTTP/1.1 200 OK\r\n{RespondWith}")
    elif StatusCode == 404:
        print(f"HTTP/1.1 404 Not Found\r\n{RespondWith}")
    elif StatusCode == 307:
        print(f"HTTP/1.1 307 Temporary Redirect\r\n{RespondWith}")



def RunServer():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(5)
    print(f"Server is listening on port {serverPort}")

    while True:
        Files=os.listdir('.')
        Files=[File for File in Files if os.path.isfile(File)]
        

        HTML=os.listdir('./HTML')
        HTML=[File for File in HTML if os.path.isfile(os.path.join('./HTML',File))]
        #print(f"HTML files: {HTML}")

        CSS=os.listdir('./CSS')
        CSS=[File for File in CSS if os.path.isfile(os.path.join('./CSS',File))]
       # print(f"CSS files: {CSS}") 

        Photos=os.listdir('./Photos')
        Photos=[File for File in Photos if os.path.isfile(os.path.join('./Photos',File))]
       #print(f"Photos files: {Photos}") 

        Videos=os.listdir('./Videos')
        Videos=[File for File in Videos if os.path.isfile(os.path.join('./Videos',File))]
        #print(f"Videos files: {Videos}")      
        

        connectionSocket, PORT = serverSocket.accept()
        IP= PORT[0]
        PortNumber= PORT[1]
        print(f"Connection from {IP} on port {PortNumber}")
        WholeRequest=connectionSocket.recv(1024).decode()

        try:
            request= WholeRequest.split('\r\n')[0]
            request=request.split(' ')[1]
            print(request)
        except:
            print("400 Bad Request")
            continue
        #respond with base HTML file for english webpage
        if request == '/' or request =='/en' or request =='/index.html' or request == 'main_en.html':
            if 'main_en.html' in HTML:
                with open('./HTML/main_en.html', 'r') as Main_English:
                    Main_English=Main_English.read()
                    ResponseSender(200,'text/html',connectionSocket)
                    connectionSocket.send(Main_English.encode())
                    
            else:
                ErrorMessage(IP, PortNumber,connectionSocket)
                

                #respond with base HTML file for arabic webpage 
        elif request =='/ar' or request =='/main_ar.html':
            if 'main_ar.html' in HTML:
                with open('./HTML/main_ar.html', 'r') as Main_Arabic:
                   Main_Arabic=Main_Arabic.read()
                   ResponseSender(200,'text/html',connectionSocket)
                   connectionSocket.send(Main_Arabic.encode())
                   
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)
            #SubPage Request English
        elif request =='/mySite_1220053_en.html':
            if 'mySite_1220053_en.html' in HTML:
                with open('./HTML/mySite_1220053_en.html', 'r') as MySite_English:
                   MySite_English=MySite_English.read()
                   ResponseSender(200,'text/html',connectionSocket)
                   connectionSocket.send(MySite_English.encode())
                   
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)
            #SubPage Request Arabic
        elif request =='/mySite_1220053_ar.html':
            if 'mySite_1220053_ar.html' in HTML:
                with open('./HTML/mySite_1220053_ar.html', 'r') as MySite_Arabic:
                   MySite_Arabic=MySite_Arabic.read()
                   ResponseSender(200,'text/html',connectionSocket)
                   connectionSocket.send(MySite_Arabic.encode())
                   
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)
        elif request =='/CSS/styles.css' or request =='/styles.css':
            if 'styles.css' in CSS:
                with open('./CSS/styles.css', 'rb') as Styles:
                   Styles=Styles.read()
                   ResponseSender(200,'text/css',connectionSocket)
                   connectionSocket.send(Styles)
                  
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)

        elif '/Photos' in request:
            ImageName=request.split('/')[-1]
            
            if ImageName in Photos:
                
                with open(f'./Photos/{ImageName}', 'rb') as img_file:
                    imgdata=img_file.read()
                    extension = ImageName.split('.')[-1].lower()
                    ResponseSender(200,f'Photos/{extension}',connectionSocket)
                    connectionSocket.send(imgdata)
                    
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)

        elif '/Videos' in request:
            Video=request.split('/')[2]
            VideoPath='./Videos/'+Video
            if Video in Videos:
                Extension='Videos/'+VideoPath.split('.')[-1]
                with open(VideoPath,'rb') as Videos:
                    Videos=Videos.read()
                    ResponseSender(200,Extension,connectionSocket)
                    connectionSocket.send(Videos)
                   
            else:
                ErrorMessage(IP,PortNumber,connectionSocket)

        elif '/Requested' in request:
            var,type= request.split('=')[1], request.split('=')[2]
            object=var.split('&')[0]
            if object in Photos and '.mp4' not in object: 
                with open(f'./Photos/{object}', 'rb') as img_file:
                    extensionImg = object.split('.')[-1].lower()
                    ResponseSender(200, f'Photos/{extensionImg}', connectionSocket)
                    connectionSocket.send(img_file.read())

            else:
                object1=object+'.jpg'
                object2=object+'.png'
                if object1 in Photos:
                    object1='./Photos/'+object1
                    with open(object1,'rb') as Photos:
                        ResponseSender(200,'Photos/jpg',connectionSocket)
                        Photos=Photos.read()
                        connectionSocket.send(Photos)
                elif object2 in Photos:
                    object2='./Photos/'+object2
                    with open(object2,'rb') as Photos:
                        ResponseSender(200,'Photos/png',connectionSocket)
                        Photos=Photos.read()
                        connectionSocket.send(Photos)

                    
            if object in Videos: 
                print("Enters Object in Videos")
                with open(f'./Videos/{object}', 'rb') as vid_file:
                    vid_data=vid_file.read()
                    extensionVid = object.split('.')[-1].lower()
                    ResponseSender(200, f'Videos/{extensionVid}', connectionSocket)
                    connectionSocket.send(vid_data)
                    

            else:
                object3=object+'.mp4'    
                if object3 in Videos:
                    object3='./Videos/'+object3
                    with open(object3,'rb') as Videos:
                        ResponseSender(200,'Videos/mp4',connectionSocket)
                        Videos=Videos.read()
                        connectionSocket.send(Videos)
                
                elif type == 'image':
                    
                    connectionSocket.send("HTTP/1.1 307 Temporary Redirect\r\n".encode())
                    connectionSocket.send('Content-Type: text/html; charset=utf-8\r\n'.encode())
                    object=object.replace(" ", "+")
                    Redirect="Location:https://www.google.com/search?q="+object+"&udm=2\r\n"
                    connectionSocket.send(Redirect.encode())
                    connectionSocket.send("\r\n".encode())
                    print("Redirecting: google search images")

                else:
                    
                    connectionSocket.send("HTTP/1.1 307 Temporary Redirect\r\n".encode())
                    connectionSocket.send('Content-Type: text/html; charset=utf-8\r\n'.encode())
                    object=object.replace(" ", "+")
                    Redirect="Location:https://www.google.com/search?q="+object+"&tbm=vid\r\n"
                    connectionSocket.send(Redirect.encode())
                    connectionSocket.send("\r\n".encode())
                    print("Redirecting: google search Videos")
             
        else:
            try:
                obj =request.split('/')[1]
                if obj in Files or obj in HTML or obj in CSS or obj in Photos or obj in Videos:
                    type=obj.split('.')[-1]
                    if obj in HTML:
                        obj='./HTML/'+obj
                    elif obj in CSS:
                        obj='./CSS/'+obj
                    elif obj in Photos:
                        obj='./Photos/'+obj
                    elif obj in Videos:
                        obj='./Videos/'+obj
                    if type == 'html':
                        ResponseSender(200,'text/html',connectionSocket)

                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                        
                    elif type =='css':
                        ResponseSender(200,'text/css',connectionSocket)

                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                    elif type == 'jpg':
                        ResponseSender(200,'Photos/jpg',connectionSocket)

                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                    elif type == 'png':
                        ResponseSender(200,'Photos/png',connectionSocket)
                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                    elif type == 'mp4':
                        ResponseSender(200,'Videos/mp4',connectionSocket)
                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                    else:
                        ResponseSender(200,'text/html',connectionSocket)
                        with open(obj,'rb') as Filess:
                            Filess=Filess.read()
                        connectionSocket.send(Filess)
                else:
                    ErrorMessage(IP,PortNumber,connectionSocket)
                    
            except IndexError:

                print("400 Bad Request")
        connectionSocket.close()
        
if __name__ == "__main__":

    RunServer()