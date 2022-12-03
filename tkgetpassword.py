#!/usr/bin/env python

"""

tkgetpassword.py

# Copyright (C) 2022 Leonardo A. Reichert
# Author: Leonardo A. Reichert
# Contact: leoreichert5000@gmail.com
# MIT license

----------------------------------------------

3 forms window password:

askcreatepassword, askoldpassword, askchangepassword

1- askcreatepassword(parent, **kw)
    Use on create a new password, return (str: a new password)

2- askoldpassword(parent, asserthash, **kw)
    Use on get old password and check with functions Sha's (HASH), return (str: old password)

3- askchangepassword(parent, asserthash, **kw)
    Use on change old password, return (str: old password, str: new passwod)

Options **kw use on the functions askcreatepassword,
        askoldpassword or askchangepassword:
    -title: optional title str
    -message: optional message str
    
    -font1: optional (font of label passwords)
    -font2: optional (font of passwords)
    
    -showchar: default is "*"
    
    -minlenght: default 0 (no limits)
    -maxlenght: default 0 (no limits)
    -onlyascii: True or False, defalt is True, validate ascii chars (0 .. 127 range)
                (from version 1.2.3)
    
    -asserthash: a string hash to authenticate (example:
            a representation hash: hashlib.new("sha256", bytesPassword).hexdigest()
            ignored by askcreatepassword(...) function
    -namesha: default used is "sha256",
            used on hashlib.new(namesha, passw).hexdisgest() method
            
    -textbutton: default is a tuple ("Ok", "Cancel")
    -stylebutton: default is "TButton"



 *** Changes, updates ***

 release 1.2.1: added variable "version"
 release 1.2.3: added optional param filter "onlyascii"
 
"""


# Copyright (C) 2022 Leonardo A. Reichert
# Author: Leonardo A. Reichert
# Contact: leoreichert5000@gmail.com
# MIT license

#MIT License
#Copyright (c) 2022 Leonardo A. Reichert

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


__all__ = [
    "askcreatepassword",
    "askoldpassword",
    "askchangepassword",
    "WinPassword",
    "version",
    ]

version = "1.2.3"



try:
    from tkinter import Toplevel,Frame,Label, BitmapImage;
    from tkinter.font import Font;
    from tkinter.ttk import Entry, Button;
except ImportError:
    from Tkinter import Toplevel,Frame,Label, BitmapImage;
    from tkFont import Font;
    from ttk import Entry, Button;


from hashlib import new as newSha; #usually used sha256
from hashlib import algorithms_available;


default_sha = "sha256";

msg_warn_forget = "Attention: passwords will be impossible to recover";

_BP_EYEOPEN = """#define image_width 21
#define image_height 21
static char image_bits[] = {
0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,
0x7f,0xc0,0x1f,0x0f,0x00,0x1e,0xc3,0x7f,0x18,0xf1,0xf3,0x11,0xf8,0xe3,0x03,
0xfc,0xe0,0x07,0xf8,0xe0,0x03,0xf1,0xf1,0x11,0xc3,0x7f,0x18,0x0f,0x00,0x1e,
0x7f,0xc0,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,
0xff,0xff,0x1f
};"""

_BP_EYECLOSE = """#define image_width 21
#define image_height 21
static char image_bits[] = {
0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0x3f,0x1e,
0x7f,0x1c,0x1e,0x0f,0x0e,0x1f,0xc3,0x87,0x19,0xf1,0xc3,0x11,0xf8,0xe1,0x03,
0xfc,0xf0,0x07,0x78,0xf8,0x03,0x39,0xfc,0x11,0x1f,0x7e,0x18,0x0f,0x03,0x1e,
0x87,0xc3,0x1f,0xc7,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,0xff,0xff,0x1f,
0xff,0xff,0x1f
};"""



def _center_window(master, window):
    window.withdraw();
    window.update_idletasks(); #<- need the geometry...

    
    xMaster, yMaster = master.winfo_rootx(),master.winfo_rooty();
    wMaster, hMaster = master.winfo_width(),master.winfo_height();
    
    xCenter, yCenter = xMaster +wMaster//2, yMaster +hMaster//2;
    
    wScreen, hScreen = master.winfo_screenwidth(),master.winfo_screenheight();
    
    w2, h2 = window.winfo_width(),window.winfo_height();
    
    x, y = xCenter-w2//2, yCenter-h2//2;
    
    x2 = x + w2;
    y2 = y + h2;
    
    if x2 > wScreen or x < 0:
        xCenter = wScreen // 2;
        x = xCenter-w2//2;
    
    if y2 > hScreen or y < 0:
        yCenter = hScreen // 2;
        y = yCenter-h2//2;
    
    window.geometry("+%d+%d" % (x, y));
    window.deiconify();


def _isAscii(string):
    for c in string:
        if ord(c) > 127:
            return False
    return True




class WinPassword(Toplevel):

    """ A class Constructor intern for create password form """
    
    def __init__(self, master_parent, **kw):

        """
            kw: -title: optional string (title of window)
                -message: (string, label top message with a classic icon warning),
                
                -font1: optional (font of labels)
                -font2: optional (font of passwords)
                
                -showchar: default is "*"
                
                -minlenght: default is 0 (no limits)
                -maxlenght: default is 0 (no limits)
                -onlyascii: True or False, defalt is True, validate ascii chars (0 .. 127 range)
                
                -asserthash: a string hash to authenticate (example:
                    a representation hash public hashlib.new("sha256", bytesPassword).hexdigest()      
                -namesha: default is "sha256",
                    used as hashlib.new(namesha, bKey).hexdisgest() method
                    
                -textbutton: default is a tuple ("Ok", "Cancel")
                -stylebutton: default is "TButton"
        """

        Toplevel.__init__(self, master_parent);

        self.withdraw(); #<- invisible
        
        self.title(kw.pop("title", "tk password"));
        self.transient(master_parent);
        self.resizable(0, 0);
        
        self.showchar = kw.pop("showchar", "*");
        
        self.asserthash = kw.pop("asserthash", "");
        self.namesha = kw.pop("namesha", default_sha);
        
        if not self.namesha in algorithms_available:
            raise Exception("Error arg value -namesha=\"%s\" not in hashlib.algorithms_available");
        
        self.minlenght = kw.pop("minlenght", 0);
        self.maxlenght = kw.pop("maxlenght", 0);
        self.onlyascii = kw.pop("onlyascii", True);
        
        assert self.minlenght >= 0 and self.maxlenght >= 0;
        
        self._nChars = 32;

        self.entrys = {};
        self.entryVars = {};
        
        self.font = kw.pop("font1", None);
        self.fontPassword = kw.pop("font2", None);

        if "message" in kw and kw["message"]:
            Label(self, bitmap="warning", compound="left",
                  text=kw["message"], font=self.font,
                  ).pack(side="top", fill="x", expand=True, padx=13);

        frameAcpt = Frame(self);
        frameAcpt.pack(side="bottom", pady=5, padx=3);
        
        self.labelError = Label(self, fg="red", font=self.font);
        self.labelError.pack(side="bottom");

        textbuttons = kw.pop("textbutton", ("Ok", "Cancel"));
        assert type(textbuttons) == tuple and len(textbuttons)==2;

        textok, textno = textbuttons;
        lenghtBtn = max(len(textok), len(textno));

        styleBtn = kw.pop("stylebutton", "TButton");
        
        btnok = Button(frameAcpt, text=textok, width=lenghtBtn, style=styleBtn,
                    command=self._accept, takefocus=False, default="active");
        btnok.grid(row=0, column=0, padx=2, ipadx=10);
        btnok.bind("<Return>", lambda e: self._accept() );

        btnno = Button(frameAcpt, text=textno, width=lenghtBtn, style=styleBtn,
               command=self.destroy, takefocus=True);
        btnno.grid(row=0, column=1, padx=2, ipadx=10);
        btnno.bind("<Return>", lambda e: self.destroy() );

        self.oldPassword = None;
        self.password = "";

        self.bpEyeClose = BitmapImage(data=_BP_EYECLOSE,foreground="gray90",background="black");
        self.bpEyeOpen = BitmapImage(data=_BP_EYEOPEN,foreground="gray90",background="black");


    def _MsgInvalidate(self):
        password = self.entrys.get("new_password").get(); #ever
        entryRee = self.entrys.get("rep_password", None); #optional
        
        entryOld = self.entrys.get("old_password", None); #optional
        
        #--- search user error ---
        if entryRee and password != entryRee.get():
            return "Error: The re-enter passwords is diferent";
        elif self.onlyascii and not _isAscii(password):
            return "Error: Invalid characters, only ASCII is accepted"

        #--- compare assert password ---
        if entryOld:
            if self.asserthash and \
                   newSha( self.namesha, (entryOld.get().encode()) ).hexdigest() != self.asserthash:
                return "Error: incorrect last password";
        
        elif self.asserthash and \
                 newSha( self.namesha, password.encode() ).hexdigest() != self.asserthash:
            return "Error: incorrect enter password";
        
        #--- compare lenght of new password ---
        if self.minlenght and len(password) < self.minlenght:
            return "Error: passwords lenght, need %d more chars" % (
                                        self.minlenght-len(password));
        
        elif self.maxlenght and len(password) > self.maxlenght:
            return "Error: The password max length is %d, cannot %d" % (self.maxlenght,
                                                                        len(password));
        
        return "";

        
    def _accept(self):
        err = self._MsgInvalidate();
        if not err:
            self.password = self.entrys["new_password"].get();
            if "old_password" in self.entrys:
                self.oldPassword = self.entrys["old_password"].get();
            self.destroy();
            return;

        self.labelError.configure(text=err);
        return;


    def createEntry(self, tagKey, prompt):
        """ constructor, this create a entry and save on self.entrys
        _MsgInvalidate method is a default invalidator """
        frame0 = Frame(self);
        frame0.pack(side="top", pady=5, padx=5);

        Label(frame0, font=self.font,text=prompt,anchor="w").pack(side="top",fill="x",padx=5);
        
        entry = Entry(frame0, font=self.fontPassword, show=self.showchar, width=32);
        entry.pack(side="left", expand="yes", fill="x");

        self.entrys[tagKey] = entry;

        entry.bind("<Return>", lambda e: self._accept() );
        entry.bind("<KeyPress>", lambda e: self.labelError.configure(text="") );
        entry.bind("<<Copy>>", lambda e: self._ignoreCopy(entry));
        
        instantBtnShow = Label(frame0, image=self.bpEyeClose);
        instantBtnShow.pack(side="right", before=entry);
        instantBtnShow.bind("<ButtonPress-1>", lambda e: self._openEye(entry, instantBtnShow));
        instantBtnShow.bind("<ButtonRelease-1>", lambda e: self._closeEye(entry, instantBtnShow));


    def _ignoreCopy(self, entry):
        if entry["show"] == self.showchar: #is hidden, cannot copy
            self.clipboard_clear();
            entry.selection_clear();
            self.bell();


    def _closeEye(self, entry, label):
        entry.configure(show=self.showchar);
        label.configure(image=self.bpEyeClose);


    def _openEye(self, entry, label):
        entry.configure(show="")
        label.configure(image=self.bpEyeOpen);

        
    def waitResp(self, exitcurgrab = True):
        """ intern function, once the form is ready,
        it show and retrieves and constrains the main focus and
        returns the response of the validated inputs """

        if exitcurgrab:
            currForm = self.grab_current();
            if currForm:
                currForm.destroy();
        
        _center_window(self.master, self);

        self.wait_visibility();
        
        first = tuple(self.entrys.keys())[0];
        self.entrys[first].focus_set();
        
        self.grab_set();
            
        self.wait_window(self);

        if self.oldPassword != None:
            return (self.oldPassword, self.password);
        
        return self.password;


    def resetClean(self):
        """ clear all entrys """
        for k in self.entrys:
            self.entrys[k].delete(0, "end");


    def __str__(self):
        """
        return "form_password" the name of a form, use to interrupt from outside
        """
        return "form_password";
    



def askcreatepassword(parent, **kw):
    """ form: create a new password, return (str: new password)"""

    kw["asserthash"]="";
    kw.setdefault("title", "Create password");
    
    context = WinPassword(parent, **kw);
    
    context.createEntry("new_password", "Password:");
    context.createEntry("rep_password", "Repeat password:");
    
    resp = context.waitResp();

    return resp;


def askoldpassword(parent, asserthash, **kw):
    """ form: get old password and check with func HASH, return (str: old password)
     param onlyascii is False by default """

    kw["asserthash"]=asserthash;
    kw.setdefault("title", "Enter password");
    kw.setdefault("onlyascii", False);
    
    context = WinPassword(parent, **kw);
    
    context.createEntry("new_password", "Enter last password:");
    
    resp = context.waitResp();

    return resp;


def askchangepassword(parent, asserthash, **kw):
    """form: change old password, return (str: old password, str: new passwod)"""
    
    kw["asserthash"]=asserthash;
    kw.setdefault("title", "Change password");
    
    context = WinPassword(parent, **kw);
    
    context.createEntry("old_password", "Last password:");
    context.createEntry("new_password", "New password:");
    context.createEntry("rep_password", "Repeat password:");
    
    resp = context.waitResp();
    
    if type(resp) != tuple:
        return ("", "");
    
    return resp; #tuple(old,new) 




if __name__ == "__main__":

    # **  Test  ** 

    try:
        from tkinter import Tk, Radiobutton;
    except:
        from Tkinter import Tk, Radiobutton;
        

    root = Tk();
    root.geometry("220x150");
    root.title("test");

    font = Font(family="Verdana", size=8);
    fontPassword = Font(family="Verdana", size=10, weight="bold");

    def test():

        typeSha = root.getvar("mysha");

        print("test, using param -namesha: %s" % typeSha);
        
        newPass = askcreatepassword(root, title="askcreatepassword(...)",
                                   minlenght=12, font1=font, font2=fontPassword);
        if not newPass:
            print("No-Password, canceled.");
            return;

        hashed = newSha(typeSha, newPass.encode()).hexdigest();
        
        print("form create password: %s %s" % (newPass, hashed) );
        
        print("form old password:", askoldpassword(root, hashed,
                                            namesha=typeSha,
                                            title="askoldpassword(...)",
                                            font1=font, font2=fontPassword),
              );
        
        oldP, newP = askchangepassword(root, hashed,
                                           namesha=typeSha,
                                           title="askchangepassword(...)",
                                           font1=font, font2=fontPassword );
        
        if not (oldP or newP):
            print("form change password is canceled");
            return;
        
        print("form change password: %s to %s" % (oldP, newP));
    
    root.setvar("mysha", default_sha);

    Radiobutton(root, text="param namesha = '%s'" %default_sha,variable="mysha",value=default_sha,
                ).pack(padx=20);
    Radiobutton(root, text="param namesha = 'sha512'", variable="mysha", value="sha512",
                ).pack(padx=20);

    Button(root, text="test", command=test).pack(pady=10);

    root.mainloop();
    




