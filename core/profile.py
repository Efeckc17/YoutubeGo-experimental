import os
import json

class UserProfile:
    def __init__(self,profile_path="user_profile.json"):
        self.profile_path=profile_path
        self.data={"name":"","profile_picture":"","default_resolution":"720p","download_path":os.getcwd(),"history_enabled":True,"theme":"Dark","proxy":"","social_media_links":{"instagram":"","twitter":"","youtube":""},"language":"en","rate_limit":None,"history":[]}
        self.load_profile()
    def load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path,"r",encoding="utf-8") as f:
                try:
                    self.data=json.load(f)
                    if "social_media_links" not in self.data:
                        self.data["social_media_links"]={"instagram":"","twitter":"","youtube":""}
                    if "history" not in self.data:
                        self.data["history"]=[]
                    self.save_profile()
                except:
                    self.save_profile()
        else:
            self.save_profile()
    def save_profile(self):
        with open(self.profile_path,"w",encoding="utf-8") as f:
            json.dump(self.data,f,indent=4)
    def set_profile(self,name,profile_picture,download_path):
        self.data["name"]=name
        self.data["profile_picture"]=profile_picture
        self.data["download_path"]=download_path
        self.save_profile()
    def set_social_links(self,instagram,twitter,youtube):
        self.data["social_media_links"]={"instagram":instagram,"twitter":twitter,"youtube":youtube}
        self.save_profile()
    def remove_profile_picture(self):
        if self.data["profile_picture"] and os.path.exists(self.data["profile_picture"]):
            try:
                os.remove(self.data["profile_picture"])
            except:
                pass
        self.data["profile_picture"]=""
        self.save_profile()
    def get_download_path(self):
        return self.data.get("download_path",os.getcwd())
    def get_proxy(self):
        return self.data.get("proxy","")
    def set_proxy(self,proxy):
        self.data["proxy"]=proxy
        self.save_profile()
    def get_theme(self):
        return self.data.get("theme","Dark")
    def set_theme(self,theme):
        self.data["theme"]=theme
        self.save_profile()
    def get_default_resolution(self):
        return self.data.get("default_resolution","720p")
    def set_default_resolution(self,resolution):
        self.data["default_resolution"]=resolution
        self.save_profile()
    def is_history_enabled(self):
        return self.data.get("history_enabled",True)
    def set_history_enabled(self,enabled):
        self.data["history_enabled"]=enabled
        self.save_profile()
    def is_profile_complete(self):
        return bool(self.data["name"])
    def set_language(self,language):
        self.data["language"]=language
        self.save_profile()
    def get_language(self):
        return self.data.get("language","en")
    def set_rate_limit(self,rate_limit):
        self.data["rate_limit"]=rate_limit
        self.save_profile()
    def get_rate_limit(self):
        return self.data.get("rate_limit",None)
    def add_history_entry(self,title,channel,url,status):
        self.data["history"].append({"title":title,"channel":channel,"url":url,"status":status})
        self.save_profile()
    def remove_history_entries(self,urls):
        self.data["history"]=[entry for entry in self.data["history"] if entry["url"] not in urls]
        self.save_profile()
    def clear_history(self):
        self.data["history"]=[]
        self.save_profile()
    def update_history_entry(self,url,new_title,new_channel,new_status=None):
        for entry in self.data["history"]:
            if entry["url"]==url:
                entry["title"]=new_title
                entry["channel"]=new_channel
                if new_status is not None:
                    entry["status"]=new_status
        self.save_profile()
