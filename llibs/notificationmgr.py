import llibs.config as config

class NotificationManager:
    def CreateBlob(self, user, msg):
        userBlob = None
        for blobItem in config.NOTIFICATIONBLOB["by"]:
            if blobItem["user"] == user:
                userBlob = blobItem
                break
        
        if userBlob:
            userBlob["unread"] += 1
            userBlob["messages"].append(msg)
        else:
            blob = {
                "unread": 1,
                "user": user,
                "messages": [msg]
            }
            config.NOTIFICATIONBLOB["by"].append(blob)
        
        config.NOTIFICATIONBLOB["unread"] += 1

    def RetrieveBlobs(self, XMPPAddress):
        formattedStrings = []
        for item in config.NOTIFICATIONBLOB["by"]:
            if XMPPAddress in str(item["user"]):
                userName = item["user"]
                messageList = item["messages"] 
                for message in messageList:
                    formattedString = f"{userName}: {message}"
                    formattedStrings.append(formattedString)
                AllMessages = "\n".join(formattedStrings)
                return AllMessages
            else:
                return "The XMPP address has to be in your contacts or have sent you a message. Try again."


    def RetrieveNotifications(self):
        summary = []
        totalUnread = 0
        for item in config.NOTIFICATIONBLOB["by"]:
            if item["unread"] > 0:
                summary.append(f" # {item['unread']} by {item['user']}")
                totalUnread += item["unread"]

        config.NOTIFICATIONBLOB["unread"] = totalUnread

        print(f"You have a total of {config.NOTIFICATIONBLOB['unread']} unread messages:")
        for line in summary:
            print(line)
        print("To read messages, type /% user@thesecure.biz.")