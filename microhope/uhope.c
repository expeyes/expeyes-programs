/* uhope: A Linux Shell for Microhope Copyright (C) 2014  A.Chatterjee    *
 * Author: A.Chatterjee <DrAmbar@gmail.com>                               *
 * GNU General Public License, version 3 (see Help-->About)                         *
 * Created: 1 Jan 2014 Last Update: 13 Jan 2014                            */
#include <gtk/gtk.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#define GETTEXT_PACKAGE "uhope"
#include <glib/gi18n-lib.h>
#include <locale.h>


#define MAX_LINE    256                                                             //Max length of a line in the editor
#define MAX_FNAME   256                                                                      //Max length of a file name
#define MAX_SRCH    256                                                                    //Max length of search string
#define MAX_STAT    512                                                                      //Max length of status line
#define MAX_FSIZE   64000           //Max file size. If its exceeded Undo and Redo wont work, but program will not crash
#define DSPL_SIZE   4096                                                   //Max size of redirected out files to display

//Global variables
gint System,StatID,UStat=0;
gchar Path[MAX_FNAME],SrchStr[MAX_SRCH]="",ReplStr[MAX_SRCH]="",FileName[MAX_FNAME]="Untitled";
gchar UBuf[2][MAX_FSIZE]={"",""},Device[MAX_FNAME]="";
GtkTextBuffer *Buf;
GtkWidget *MWin,*TextView,*StatBar,*FindEntry,*ChCase,*ChWrap,*RFind,*RRepl,*RChCase,*RChWrap;
gboolean CaseMatch=FALSE,WrapAround=TRUE,Located,UnsavedChanges=FALSE,MaskBufChg=FALSE,
         SubsAll=FALSE,Push=FALSE;
//----------------------------------------------------------------------------------------------------------------------
void Attention(gchar *Messg,gboolean Scroll)                     //Displays message. Set Scroll to TRUE for big messages
{
GtkWidget *W,*ScrlW,*Label,*But;

W=gtk_dialog_new();
gtk_window_set_modal(GTK_WINDOW(W),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(W),GTK_WINDOW(MWin));
 gtk_window_set_title(GTK_WINDOW(W),_("Message"));
gtk_container_set_border_width(GTK_CONTAINER(W),10);

if (Scroll)
   {
   ScrlW=gtk_scrolled_window_new(NULL,NULL);
   gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(ScrlW),GTK_POLICY_NEVER,GTK_POLICY_AUTOMATIC);
   gtk_widget_set_size_request(GTK_WIDGET(ScrlW),-1,300);
   gtk_box_pack_start(GTK_BOX(GTK_DIALOG(W)->vbox),ScrlW,TRUE,TRUE,0);
   }

Label=gtk_label_new(Messg);
if (Scroll) gtk_scrolled_window_add_with_viewport(GTK_SCROLLED_WINDOW(ScrlW),Label);
else gtk_box_pack_start(GTK_BOX(GTK_DIALOG(W)->vbox),Label,FALSE,FALSE,0);
But=gtk_button_new_from_stock(GTK_STOCK_OK);
gtk_box_pack_start(GTK_BOX(GTK_DIALOG(W)->action_area),But,TRUE,FALSE,0);
g_signal_connect_object(But,"clicked",G_CALLBACK(gtk_widget_destroy),GTK_OBJECT(W),G_CONNECT_SWAPPED);
gtk_widget_show_all(W);
}
//----------------------------------------------------------------------------------------------------------------------
void Dspl(gchar *What,gint Status,gboolean Scroll)                                        //Shows the output of system()
{
FILE *Fp;
gchar Out[DSPL_SIZE],Line[256],StatusLine[MAX_STAT];

 if (Status) sprintf(Out,_("ERROR:%s\n"),What); else sprintf(Out,_("SUCCESS:%s\n"),What); 
if (!(Fp=fopen("out.txt","r"))) return;
while (TRUE)
   {
     if (strlen(Out)>(DSPL_SIZE-250)) { strcat(Out,_("...output too big, view truncated")); break; }
   if (!fgets(Line,255,Fp)) break;
   strcat(Out,Line);
   }
fclose(Fp);
Attention(Out,Scroll);
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 if (!Status) sprintf(StatusLine,_("%s %s was successful"),FileName,What);
 else sprintf(StatusLine,_("%s of %s failed"),What,FileName);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
UnsavedChanges=FALSE;
}
//----------------------------------------------------------------------------------------------------------------------
void ShowDevice()
{
gchar StatusLine[MAX_STAT],Title[128];

gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
if (strlen(Device)==0)
   {
     strcpy(Title,_("uhope - No device detected"));
     strcpy(StatusLine,_("No device detected"));
   }
else
   {
     sprintf(Title,_("uhope - Device:%s"),Device);
     sprintf(StatusLine,_("Device:%s"),Device);
   }
gtk_window_set_title(GTK_WINDOW(MWin),Title);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
}
//----------------------------------------------------------------------------------------------------------------------
void DeviceSelected(GtkComboBoxText *Combo,gpointer Data)
{
gchar *Str;

Str=gtk_combo_box_text_get_active_text(Combo);
strcpy(Device,Str); g_free(Str);
ShowDevice();
}
//----------------------------------------------------------------------------------------------------------------------
void DetectHardware(GtkWidget *W,gpointer Unused)
{
DIR *D;
struct dirent *Dir;
gchar DName[5][MAX_FNAME],Str[128];
gint i,N;
GtkWidget *Win,*VBox,*HBox,*Label,*Combo,*But;

D=opendir("/dev/"); N=0;
if (!D) return;
while ((Dir=readdir(D)))
   {
   if (!strncmp("ttyACM",Dir->d_name,6) || !strncmp("ttyUSB",Dir->d_name,6))
      { strcpy(DName[N],Dir->d_name); ++N; }
   if (N>4) break;
   }
closedir(D);

 if (N==0) { Attention(_("No device detected!"),FALSE); strcpy(Device,""); ShowDevice(); return; }
if (N==1)
   {
     sprintf(Device,"/dev/%s",DName[0]); sprintf(Str,_("Device detected: %s"),Device);
   Attention(Str,FALSE); ShowDevice(); return;
   }

Win=gtk_window_new(GTK_WINDOW_TOPLEVEL);
gtk_window_set_modal(GTK_WINDOW(Win),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(Win),GTK_WINDOW(MWin));
 gtk_window_set_title(GTK_WINDOW(Win),_("Select Microhope device"));
gtk_window_set_position(GTK_WINDOW(Win),GTK_WIN_POS_CENTER);
VBox=gtk_vbox_new(FALSE,10);
gtk_container_set_border_width(GTK_CONTAINER(VBox),10);
gtk_container_add(GTK_CONTAINER(Win),VBox);

 Label=gtk_label_new(_("Multiple devices.\nPlease select Microhope from the list:"));
gtk_box_pack_start(GTK_BOX(VBox),Label,FALSE,FALSE,0);
Combo=gtk_combo_box_text_new_with_entry();

HBox=gtk_hbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(VBox),HBox,FALSE,FALSE,0);
for (i=0;i<N;++i) { sprintf(Str,"/dev/%s",DName[i]); gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(Combo),Str); }

g_signal_connect(G_OBJECT(Combo),"changed",G_CALLBACK(DeviceSelected),NULL);
gtk_box_pack_start(GTK_BOX(HBox),Combo,FALSE,FALSE,0);

HBox=gtk_hbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(VBox),HBox,FALSE,FALSE,0);
But=gtk_button_new_from_stock(GTK_STOCK_OK); gtk_box_pack_start(GTK_BOX(HBox),But,TRUE,FALSE,0);
g_signal_connect_swapped(But,"clicked",G_CALLBACK(gtk_widget_destroy),Win);

gtk_widget_show_all(Win);
}
//----------------------------------------------------------------------------------------------------------------------
void Upload(GtkWidget *W,gpointer Unused)
{
gchar BaseFName[MAX_FNAME],HexFName[MAX_FNAME],Cmd[1024];
gint Status;
FILE *Fp;

 if (!strcmp(FileName,"Untitled")) { Attention(_("ERROR: No file loaded!"),FALSE); return; }
strcpy(BaseFName,FileName); BaseFName[strlen(FileName)-2]='\0';
sprintf(HexFName,"%s.hex",BaseFName);
 if (!(Fp=fopen(HexFName,"r"))) { Attention(_("ERROR: No hex file. Compile first!"),FALSE); return; }
else fclose(Fp);
 if (strlen(Device)==0) { Attention(_("ERROR: Please Detect Hardware first!"),FALSE); return; }

sprintf(Cmd,"avrdude -b 19200 -P %s -pm32 -c stk500v1 -U flash:w:%s 1>out.txt 2>>out.txt",Device,HexFName);
Status=system(Cmd);
 Dspl(_("Upload"),Status,TRUE);
return;
}
//----------------------------------------------------------------------------------------------------------------------
void FileOpen(GtkWidget *W,gpointer Unused)
{
GtkWidget *Dialog;
GtkFileFilter *FilterC,*FilterS,*FilterT,*FilterO,*FilterA;
gchar Line[MAX_LINE],StatusLine[MAX_STAT];
FILE *Fp;
GtkTextIter Start,End;
gchar *P;

 Dialog=gtk_file_chooser_dialog_new(_("Open File"),GTK_WINDOW(MWin),GTK_FILE_CHOOSER_ACTION_OPEN,
       GTK_STOCK_CANCEL,GTK_RESPONSE_CANCEL,GTK_STOCK_OPEN,GTK_RESPONSE_ACCEPT,NULL);
gtk_file_chooser_set_current_folder(GTK_FILE_CHOOSER(Dialog),Path);

 FilterC=gtk_file_filter_new(); gtk_file_filter_set_name(FilterC,_("C source (*.c)"));
gtk_file_filter_add_pattern(FilterC,"*.c"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterC);
 FilterS=gtk_file_filter_new(); gtk_file_filter_set_name(FilterS,_("Asm (*.S,*.s)"));
gtk_file_filter_add_pattern(FilterS,"*.S"); gtk_file_filter_add_pattern(FilterS,"*.s");
gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterS);
 FilterT=gtk_file_filter_new(); gtk_file_filter_set_name(FilterT,_("Text (*.txt)"));
gtk_file_filter_add_pattern(FilterT,"*.txt"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterT);
 FilterO=gtk_file_filter_new(); gtk_file_filter_set_name(FilterO,_("Obj Dump (*.lst)"));
gtk_file_filter_add_pattern(FilterO,"*.lst"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterO);
 FilterA=gtk_file_filter_new(); gtk_file_filter_set_name(FilterA,_("All types (*.*)"));
gtk_file_filter_add_pattern(FilterA,"*.*"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterA);

if (gtk_dialog_run(GTK_DIALOG(Dialog)) == GTK_RESPONSE_ACCEPT)
  {
  gchar *FName;
  FName=gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(Dialog));
  Fp=fopen(FName,"r");
  gtk_text_buffer_set_text(Buf,"",-1);
  while (TRUE)
     {
     if (fgets(Line,MAX_LINE-1,Fp)==NULL) break;
     gtk_text_buffer_get_end_iter(Buf,&End);
     gtk_text_buffer_insert(Buf,&End,Line,strlen(Line));
     }
  fclose(Fp); strcpy(FileName,FName); g_free(FName);
  if ((P=strrchr(FileName,'/'))) { strcpy(Path,FileName); Path[P-FileName]='\0'; }        //Store the path for next time
  }
gtk_widget_destroy(Dialog);

gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_place_cursor(Buf,&Start);         //Position cursor at start
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
strcpy(StatusLine,FileName); gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
UnsavedChanges=FALSE;
}
//----------------------------------------------------------------------------------------------------------------------
void FileNew(GtkWidget *W,gpointer Unused)
{
gchar StatusLine[MAX_STAT];

gtk_text_buffer_set_text(Buf,"",-1);
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 strcpy(FileName,_("Untitled")); strcpy(StatusLine,FileName);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
UnsavedChanges=FALSE;
}
//----------------------------------------------------------------------------------------------------------------------
void FileSaveAs(GtkWidget *W,gpointer Unused)
{
GtkWidget *Dialog;
GtkFileFilter *FilterC,*FilterS,*FilterT,*FilterA;
FILE *Fp;
GtkTextIter Start,End;
gchar *BufText,StatusLine[MAX_STAT];

gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufText=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);

Dialog=gtk_file_chooser_dialog_new("Save As",GTK_WINDOW(MWin),GTK_FILE_CHOOSER_ACTION_SAVE,
       GTK_STOCK_CANCEL,GTK_RESPONSE_CANCEL,GTK_STOCK_SAVE,GTK_RESPONSE_ACCEPT,NULL);

gtk_file_chooser_set_current_folder(GTK_FILE_CHOOSER(Dialog),Path);

 FilterC=gtk_file_filter_new(); gtk_file_filter_set_name(FilterC,_("C source (*.c)"));
gtk_file_filter_add_pattern(FilterC,"*.c"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterC);
 FilterS=gtk_file_filter_new(); gtk_file_filter_set_name(FilterS,_("Asm (*.S,*.s)"));
gtk_file_filter_add_pattern(FilterS,"*.S"); gtk_file_filter_add_pattern(FilterS,"*.s");
gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterS);
 FilterT=gtk_file_filter_new(); gtk_file_filter_set_name(FilterT,_("Text (*.txt)"));
gtk_file_filter_add_pattern(FilterT,"*.txt"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterT);
 FilterA=gtk_file_filter_new(); gtk_file_filter_set_name(FilterA,_("All types (*.*)"));
gtk_file_filter_add_pattern(FilterA,"*.*"); gtk_file_chooser_add_filter(GTK_FILE_CHOOSER(Dialog),FilterA);

gtk_file_chooser_set_do_overwrite_confirmation(GTK_FILE_CHOOSER(Dialog),TRUE);
 if (strcmp(FileName,_("Untitled"))) gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(Dialog),FileName);
if (gtk_dialog_run(GTK_DIALOG(Dialog)) == GTK_RESPONSE_ACCEPT)
  {
  gchar *FName;
  FName=gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(Dialog));
  Fp=fopen(FName,"w"); fputs(BufText,Fp); fclose(Fp);
  strcpy(FileName,FName); g_free(FName);
  gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
  sprintf(StatusLine,_("%s saved"),FileName); gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
  UnsavedChanges=FALSE;
  }
gtk_widget_destroy(Dialog);
}
//----------------------------------------------------------------------------------------------------------------------
void FileSave(GtkWidget *W,gpointer Unused)
{
FILE *Fp;
GtkTextIter Start,End;
gchar *BufText,StatusLine[MAX_STAT];

 if (!strcmp(FileName,_("Untitled"))) { FileSaveAs(W,Unused); return; }
gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufText=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
Fp=fopen(FileName,"w"); fputs(BufText,Fp); fclose(Fp);
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 sprintf(StatusLine,_("%s saved"),FileName); gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
UnsavedChanges=FALSE;
}
//----------------------------------------------------------------------------------------------------------------------
void Compile(GtkWidget *W,gpointer Unused)
{
gchar BaseFName[MAX_FNAME],FType[5],Cmd[1024];
gint Status,L;

 if (!strcmp(FileName,_("Untitled"))) { Attention(_("ERROR: No C file loaded!"),FALSE); return; }
L=strlen(FileName);
strcpy(BaseFName,FileName); BaseFName[L-2]='\0'; strcpy(FType,&FileName[L-2]);
 if (strcmp(FType,".c")) { Attention(_("ERROR: The loaded file type is not .c"),FALSE); return; }
if (UnsavedChanges) FileSave(NULL,NULL);
sprintf(Cmd,"avr-gcc -Wall -O2 -mmcu=atmega32 -o %s %s 1>out.txt 2>>out.txt",BaseFName,FileName);
Status=system(Cmd);
 if (Status!=0) { Dspl(_("Compilation"),Status,FALSE); return; }
sprintf(Cmd,"avr-objcopy -j .text -j .data -O ihex %s %s.hex 1>>out.txt 2>>out.txt",BaseFName,BaseFName);
Status=system(Cmd);
 Dspl(_("Compilation"),Status,FALSE);
sprintf(Cmd,"avr-objdump -S %s >%s.lst",BaseFName,BaseFName);
Status=system(Cmd);
}
//----------------------------------------------------------------------------------------------------------------------
void Assemble(GtkWidget *W,gpointer Unused)
{
gchar BaseFName[MAX_FNAME],FType[5],Cmd[1024];
gint Status,L;

 if (!strcmp(FileName,"Untitled")) { Attention(_("ERROR: No assembler file loaded!"),FALSE); return; }
L=strlen(FileName);
strcpy(BaseFName,FileName); BaseFName[L-2]='\0'; strcpy(FType,&FileName[L-2]);
if (strcmp(FType,".S") && strcmp(FType,".s"))
  { Attention(_("ERROR: The loaded file type is not .S or .s"),FALSE); return; }
if (UnsavedChanges) FileSave(NULL,NULL);
sprintf(Cmd,"avr-gcc -Wall -O2 -mmcu=atmega32 -o %s %s 1>out.txt 2>>out.txt",BaseFName,FileName);
Status=system(Cmd);
 if (Status!=0) { Dspl(_("Assembly"),Status,FALSE); return; }
sprintf(Cmd,"avr-objcopy -j .text -j .data -O ihex %s %s.hex 1>>out.txt 2>>out.txt",BaseFName,BaseFName);
Status=system(Cmd);
 Dspl(_("Assembly"),Status,FALSE);
sprintf(Cmd,"avr-objdump -S %s >%s.lst",BaseFName,BaseFName);
Status=system(Cmd);
}
//----------------------------------------------------------------------------------------------------------------------
void EditDelete(GtkWidget *W,gpointer Unused)
{
GtkTextIter Start,End;

if (gtk_text_buffer_get_selection_bounds(Buf,&Start,&End)) gtk_text_buffer_delete(Buf,&Start,&End);
}
//----------------------------------------------------------------------------------------------------------------------
void EditCopy(GtkWidget *W,gpointer Unused)
{
GtkClipboard *ClipBoard;

ClipBoard=gtk_clipboard_get(GDK_NONE);
gtk_text_buffer_copy_clipboard(Buf,ClipBoard);
}
//----------------------------------------------------------------------------------------------------------------------
void EditCut(GtkWidget *W,gpointer Unused)
{
GtkClipboard *ClipBoard;
GtkTextIter Start,End;
gchar *BufTxt;

MaskBufChg=TRUE;                                                                         //Ensure BufferChanged wont act
gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufTxt=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
if (strlen(BufTxt)<MAX_FSIZE-1) { strcpy(UBuf[UStat],BufTxt); UStat=1-UStat; }                          //Update UndoBuf

ClipBoard=gtk_clipboard_get(GDK_NONE);
gtk_text_buffer_cut_clipboard(Buf,ClipBoard,TRUE);

MaskBufChg=FALSE;                                                                                         //Restore flag
}
//----------------------------------------------------------------------------------------------------------------------
void EditPaste(GtkWidget *W,gpointer Unused)
{
GtkClipboard *ClipBoard;
GtkTextIter Start,End;
gchar *BufTxt;

MaskBufChg=TRUE;                                                                         //Ensure BufferChanged wont act
gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufTxt=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
if (strlen(BufTxt)<MAX_FSIZE-1) { strcpy(UBuf[UStat],BufTxt); UStat=1-UStat; }                          //Update UndoBuf

ClipBoard=gtk_clipboard_get(GDK_NONE);
gtk_text_buffer_paste_clipboard(Buf,ClipBoard,NULL,TRUE);

MaskBufChg=FALSE;                                                                                         //Restore flag
}
//----------------------------------------------------------------------------------------------------------------------
gchar* StrStrI(gchar *S1,gchar *S2)
{
gint i,j,k;

for (i=0;S1[i];++i) for (j=i,k=0;tolower(S1[j])==tolower(S2[k]);j++,k++)
if (!S2[k+1]) return (S1+i);
return NULL;
}
//----------------------------------------------------------------------------------------------------------------------
void FindNext(GtkWidget *W,gpointer Unused)
{
gchar *BufTxt1,*BufTxt2,*P,StatusLine[MAX_STAT];
GtkTextIter Start,EndSel,End;
GtkTextMark *Mark,*Pos;
gint FindStart,FindEnd,CurOfs;
gboolean Found,Wrapped;

if (!strlen(SrchStr)) { Located=FALSE; return; }

Mark=gtk_text_buffer_get_mark(Buf,"selection_bound");    //Mark at end-of-selection (or cursor position if no selection)
gtk_text_buffer_get_iter_at_mark(Buf,&EndSel,Mark);                               //Iter at end-of-selection (or cursor)
gtk_text_buffer_get_start_iter(Buf,&Start);                                                     //Iter at start position
gtk_text_buffer_get_end_iter(Buf,&End);                                                           //Iter at end position
BufTxt1=gtk_text_buffer_get_text(Buf,&Start,&EndSel,FALSE);            //Text from start to end-of-selection (or cursor)
BufTxt2=gtk_text_buffer_get_text(Buf,&EndSel,&End,FALSE);                //Text from end-of-selection (or cursor) to end
CurOfs=strlen(BufTxt1);                                                         //Offset to end-of-selection (or cursor)

if (CaseMatch) P=strstr(BufTxt2,SrchStr); else P=StrStrI(BufTxt2,SrchStr);
if (!P)
   {
   Found=FALSE;
   if (WrapAround && !SubsAll)                                                       //SubsAll flag set in SubstituteAll
      {
      if (CaseMatch) P=strstr(BufTxt1,SrchStr); else P=StrStrI(BufTxt1,SrchStr);
      CurOfs=0;
      if (!P) Found=FALSE; else { Found=TRUE; Wrapped=TRUE; }
      }
   }
else { Found=TRUE; Wrapped=FALSE; }

if (!Found)
   {
   Located=FALSE;
   gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
   sprintf(StatusLine,_("%s not found"),SrchStr);
   gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
   }
else
   {
   Located=TRUE;
   if (Wrapped) FindStart=(gint)(P-BufTxt1)+CurOfs; else FindStart=(gint)(P-BufTxt2)+CurOfs;
   FindEnd=FindStart+strlen(SrchStr);
   gtk_text_buffer_get_iter_at_offset(Buf,&Start,FindStart);
   gtk_text_buffer_get_iter_at_offset(Buf,&End,FindEnd);
   gtk_text_buffer_select_range(Buf,&Start,&End);
   Pos=gtk_text_buffer_create_mark(Buf,"Pos",&End,FALSE);
   gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(TextView),Pos);
   if (Wrapped) sprintf(StatusLine,_("%s found after wrap"),SrchStr); else sprintf(StatusLine,"%s found",SrchStr);
   gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
   gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
   }
}
//----------------------------------------------------------------------------------------------------------------------
void Find(GtkWidget *W,gpointer Unused)
{
const gchar *FTxt;
gchar *BufTxt1,*BufTxt2,*P,StatusLine[MAX_STAT];
GtkTextIter Start,EndSel,End;
GtkTextMark *Mark,*Pos;
gint FindStart,FindEnd,CurOfs;
gboolean Found,Wrapped;

FTxt=gtk_entry_get_text(GTK_ENTRY(FindEntry));
if (!strlen(FTxt)) return;
strcpy(SrchStr,FTxt);
if (GTK_TOGGLE_BUTTON(ChCase)->active) CaseMatch =TRUE; else CaseMatch =FALSE;
if (GTK_TOGGLE_BUTTON(ChWrap)->active) WrapAround=TRUE; else WrapAround=FALSE;

 Mark=gtk_text_buffer_get_mark(Buf,"selection_bound");    //Mark at end-of-selection (or cursor position if no selection)
gtk_text_buffer_get_iter_at_mark(Buf,&EndSel,Mark);                               //Iter at end-of-selection (or cursor)
gtk_text_buffer_get_start_iter(Buf,&Start);                                                     //Iter at start position
gtk_text_buffer_get_end_iter(Buf,&End);                                                           //Iter at end position
BufTxt1=gtk_text_buffer_get_text(Buf,&Start,&EndSel,FALSE);            //Text from start to end-of-selection (or cursor)
BufTxt2=gtk_text_buffer_get_text(Buf,&EndSel,&End,FALSE);                //Text from end-of-selection (or cursor) to end
CurOfs=strlen(BufTxt1);                                                         //Offset to end-of-selection (or cursor)

if (CaseMatch) P=strstr(BufTxt2,SrchStr); else P=StrStrI(BufTxt2,SrchStr);
if (!P)
   {
   Found=FALSE;
   if (WrapAround)
      {
      if (CaseMatch) P=strstr(BufTxt1,SrchStr); else P=StrStrI(BufTxt1,SrchStr);
      CurOfs=0;
      if (!P) Found=FALSE; else { Found=TRUE; Wrapped=TRUE; }
      }
   }
else { Found=TRUE; Wrapped=FALSE; }

if (!Found)
   {
     sprintf(StatusLine,_("%s not found"),FTxt);
   gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
   gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
   }
else
   {
   if (Wrapped) FindStart=(gint)(P-BufTxt1)+CurOfs; else FindStart=(gint)(P-BufTxt2)+CurOfs;
   FindEnd=FindStart+strlen(FTxt);
   gtk_text_buffer_get_iter_at_offset(Buf,&Start,FindStart);
   gtk_text_buffer_get_iter_at_offset(Buf,&End,FindEnd);
   gtk_text_buffer_select_range(Buf,&Start,&End);
   Pos=gtk_text_buffer_create_mark(Buf,"Pos",&End,FALSE);
   gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(TextView),Pos);
   if (Wrapped) sprintf(StatusLine,_("%s found after wrap"),FTxt); else sprintf(StatusLine,"%s found",FTxt);
   gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
   gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
   }
}
//----------------------------------------------------------------------------------------------------------------------
void EditFind(GtkWidget *W,gpointer Unused)
{
GtkWidget *FWin,*HBox,*VBox,*VBox0,*VBox1,*VBox2,*Label,*But;

FWin=gtk_window_new(GTK_WINDOW_TOPLEVEL);
gtk_window_set_modal(GTK_WINDOW(FWin),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(FWin),GTK_WINDOW(MWin));
 gtk_window_set_title(GTK_WINDOW(FWin),_("Find"));
gtk_window_set_position(GTK_WINDOW(FWin),GTK_WIN_POS_CENTER);

VBox0=gtk_vbox_new(FALSE,0); gtk_container_add(GTK_CONTAINER(FWin),VBox0);
HBox=gtk_hbox_new(FALSE,10); gtk_container_add(GTK_CONTAINER(VBox0),HBox);
gtk_container_set_border_width(GTK_CONTAINER(HBox),10);

VBox1=gtk_vbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(HBox),VBox1,FALSE,FALSE,0);
VBox2=gtk_vbox_new(FALSE,10); gtk_box_pack_start(GTK_BOX(HBox),VBox2,FALSE,FALSE,0);

HBox=gtk_hbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(VBox1),HBox,FALSE,FALSE,0);
 Label=gtk_label_new(_("Text to Find:")); gtk_box_pack_start(GTK_BOX(HBox),Label,FALSE,FALSE,0);

FindEntry=gtk_entry_new();
gtk_entry_set_max_length(GTK_ENTRY(FindEntry),MAX_SRCH-1);
gtk_box_pack_start(GTK_BOX(VBox1),FindEntry,FALSE,FALSE,0);
gtk_entry_set_text(GTK_ENTRY(FindEntry),SrchStr);

VBox=gtk_vbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(VBox1),VBox,FALSE,FALSE,10);
 ChCase=gtk_check_button_new_with_label(_("Match case")); gtk_box_pack_start(GTK_BOX(VBox),ChCase,FALSE,FALSE,0);
if (CaseMatch) gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(ChCase),TRUE);
else           gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(ChCase),FALSE);
 ChWrap=gtk_check_button_new_with_label(_("Wrap around")); gtk_box_pack_start(GTK_BOX(VBox),ChWrap,FALSE,FALSE,0);
if (WrapAround) gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(ChWrap),TRUE);
else            gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(ChWrap),FALSE);

 But=gtk_button_new_with_label(_("Find")); gtk_box_pack_start(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect(But,"clicked",G_CALLBACK(Find),NULL);

But=gtk_button_new_from_stock(GTK_STOCK_CLOSE); gtk_box_pack_end(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect_swapped(But,"clicked",G_CALLBACK(gtk_widget_destroy),FWin);

gtk_widget_show_all(FWin);
}
//----------------------------------------------------------------------------------------------------------------------
void SelectAll(GtkWidget *W,gpointer Unused)
{
GtkTextIter Start,End;

gtk_text_buffer_get_start_iter(Buf,&Start);                                                     //Iter at start position
gtk_text_buffer_get_end_iter(Buf,&End);                                                           //Iter at end position
gtk_text_buffer_select_range(Buf,&Start,&End);                                                //Select from Start to End
}
//----------------------------------------------------------------------------------------------------------------------
void Substitute(GtkWidget *W,gpointer Unused)
{
const gchar *FTxt,*RTxt;
GtkTextMark *Mark;
GtkTextIter Start,End,SelStart,SelEnd;
gchar *BufTxt,*BufTxt1,*BufTxt2,*BTxt,StatusLine[MAX_STAT];
gint L1,L2;

FTxt=gtk_entry_get_text(GTK_ENTRY(RFind)); if (!strlen(FTxt)) return;
RTxt=gtk_entry_get_text(GTK_ENTRY(RRepl));
strcpy(SrchStr,FTxt); strcpy(ReplStr,RTxt);
if (GTK_TOGGLE_BUTTON(RChCase)->active) CaseMatch =TRUE; else CaseMatch =FALSE;
if (GTK_TOGGLE_BUTTON(RChWrap)->active) WrapAround=TRUE; else WrapAround=FALSE;
FindNext(W,NULL); if (!Located) return;

MaskBufChg=TRUE;                                                                   //Ensure that BufferChanged wont act
gtk_text_buffer_get_start_iter(Buf,&Start);                                                              //Iter at start
gtk_text_buffer_get_end_iter(Buf,&End);                                                                    //Iter at end
if (!SubsAll)                                                  //Update UndoBuf unless SubstituteAll has already done it
   {
   BufTxt=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
   if (strlen(BufTxt)<MAX_FSIZE-1) { strcpy(UBuf[UStat],BufTxt); UStat=1-UStat; }
   }

Mark=gtk_text_buffer_get_mark(Buf,"insert"); gtk_text_buffer_get_iter_at_mark(Buf,&SelStart,Mark);  //Start of selection
Mark=gtk_text_buffer_get_mark(Buf,"selection_bound"); gtk_text_buffer_get_iter_at_mark(Buf,&SelEnd,Mark);   //End of sel
BufTxt1=gtk_text_buffer_get_text(Buf,&Start,&SelStart,FALSE);                    //Text from start to start-of-selection
BufTxt2=gtk_text_buffer_get_text(Buf,&SelEnd,&End,FALSE);                            //Text from end-of-selection to end

L1=strlen(BufTxt1); L2=strlen(RTxt);
BTxt=g_malloc(L1+L2+strlen(BufTxt2)+10);
strcpy(BTxt,BufTxt1); strcat(BTxt,RTxt); strcat(BTxt,BufTxt2);
gtk_text_buffer_set_text(Buf,BTxt,-1); g_free(BTxt);

gtk_text_buffer_get_iter_at_offset(Buf,&SelStart,L1);
gtk_text_buffer_get_iter_at_offset(Buf,&SelEnd,L1+L2);
gtk_text_buffer_select_range(Buf,&SelStart,&SelEnd);
Mark=gtk_text_buffer_create_mark(Buf,"Pos",&SelEnd,FALSE);
gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(TextView),Mark);

gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 sprintf(StatusLine,_("%s replaced by %s"),FTxt,RTxt);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
MaskBufChg=FALSE;                                                                                   //Restore this flag
}
//----------------------------------------------------------------------------------------------------------------------
void SubstituteAll(GtkWidget *W,gpointer Unused)
{
GtkTextIter Start,End;
GtkTextMark *Mark;
gint i;
gchar StatusLine[MAX_STAT],*BufTxt;
const gchar *FTxt;

FTxt=gtk_entry_get_text(GTK_ENTRY(RFind)); if (!strlen(FTxt)) return;
MaskBufChg=TRUE; SubsAll=TRUE;                                  //Ensure BufferChanged wont act and Substitute wont wrap
gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufTxt=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
if (strlen(BufTxt)<MAX_FSIZE-1) { strcpy(UBuf[UStat],BufTxt); UStat=1-UStat; }                          //Update UndoBuf

gtk_text_buffer_select_range(Buf,&Start,&Start);                                                  //Move cursor to start
for (i=0;i<1000;++i) { Substitute(W,NULL); if (!Located) break; }                  //Repeat substitutions. Limit to 1000
gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_select_range(Buf,&Start,&Start);      //Move cursor to start
Mark=gtk_text_buffer_create_mark(Buf,"Start",&Start,FALSE);                                              //Mark at start
gtk_text_view_scroll_mark_onscreen(GTK_TEXT_VIEW(TextView),Mark);                                      //Scroll to start
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 sprintf(StatusLine,_("%d replacements made"),i);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);                             //Display no. of substitutions
MaskBufChg=FALSE; SubsAll=FALSE;                                                                   //Restore these flags
}
//----------------------------------------------------------------------------------------------------------------------
void RFindNext(GtkWidget *W,gpointer Unused)
{
const gchar *FTxt;

FTxt=gtk_entry_get_text(GTK_ENTRY(RFind));
if (!strlen(FTxt)) return;
strcpy(SrchStr,FTxt);
if (GTK_TOGGLE_BUTTON(RChCase)->active) CaseMatch =TRUE; else CaseMatch =FALSE;
if (GTK_TOGGLE_BUTTON(RChWrap)->active) WrapAround=TRUE; else WrapAround=FALSE;
FindNext(W,Unused);
}
//----------------------------------------------------------------------------------------------------------------------
void EditReplace(GtkWidget *W,gpointer Unused)
{
GtkWidget *RWin,*HBox,*VBox,*VBox0,*VBox1,*VBox2,*Label,*But;

RWin=gtk_window_new(GTK_WINDOW_TOPLEVEL);
gtk_window_set_modal(GTK_WINDOW(RWin),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(RWin),GTK_WINDOW(MWin));
gtk_window_set_title(GTK_WINDOW(RWin),"Replace");
gtk_window_set_position(GTK_WINDOW(RWin),GTK_WIN_POS_CENTER);

VBox0=gtk_vbox_new(FALSE,0); gtk_container_add(GTK_CONTAINER(RWin),VBox0);
HBox=gtk_hbox_new(FALSE,10); gtk_container_add(GTK_CONTAINER(VBox0),HBox);
gtk_container_set_border_width(GTK_CONTAINER(HBox),10);

VBox1=gtk_vbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(HBox),VBox1,FALSE,FALSE,0);
VBox2=gtk_vbox_new(FALSE,10); gtk_box_pack_start(GTK_BOX(HBox),VBox2,FALSE,FALSE,0);

HBox=gtk_hbox_new(FALSE,24); gtk_box_pack_start(GTK_BOX(VBox1),HBox,FALSE,FALSE,0);
Label=gtk_label_new("Find what:"); gtk_box_pack_start(GTK_BOX(HBox),Label,FALSE,FALSE,0);
RFind=gtk_entry_new(); gtk_entry_set_max_length(GTK_ENTRY(RFind),MAX_SRCH-1);
gtk_box_pack_start(GTK_BOX(HBox),RFind,FALSE,FALSE,0);
gtk_entry_set_text(GTK_ENTRY(RFind),SrchStr);

HBox=gtk_hbox_new(FALSE,5); gtk_box_pack_start(GTK_BOX(VBox1),HBox,FALSE,FALSE,0);
Label=gtk_label_new("Replace with:"); gtk_box_pack_start(GTK_BOX(HBox),Label,FALSE,FALSE,0);
RRepl=gtk_entry_new(); gtk_entry_set_max_length(GTK_ENTRY(RRepl),MAX_SRCH-1);
gtk_box_pack_start(GTK_BOX(HBox),RRepl,FALSE,FALSE,0);
gtk_entry_set_text(GTK_ENTRY(RRepl),ReplStr);

VBox=gtk_vbox_new(FALSE,0); gtk_box_pack_start(GTK_BOX(VBox1),VBox,FALSE,FALSE,10);
 RChCase=gtk_check_button_new_with_label(_("Match case")); gtk_box_pack_start(GTK_BOX(VBox),RChCase,FALSE,FALSE,0);
if (CaseMatch) gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(RChCase),TRUE);
else           gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(RChCase),FALSE);
 RChWrap=gtk_check_button_new_with_label(_("Wrap around")); gtk_box_pack_start(GTK_BOX(VBox),RChWrap,FALSE,FALSE,0);
if (WrapAround) gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(RChWrap),TRUE);
else            gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(RChWrap),FALSE);

 But=gtk_button_new_with_label(_("Find Next")); gtk_box_pack_start(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect(But,"clicked",G_CALLBACK(RFindNext),NULL);

 But=gtk_button_new_with_label(_("Replace")); gtk_box_pack_start(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect(But,"clicked",G_CALLBACK(Substitute),NULL);

 But=gtk_button_new_with_label(_("Replace All")); gtk_box_pack_start(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect(But,"clicked",G_CALLBACK(SubstituteAll),NULL);

But=gtk_button_new_from_stock(GTK_STOCK_CLOSE); gtk_box_pack_end(GTK_BOX(VBox2),But,FALSE,FALSE,0);
g_signal_connect_swapped(But,"clicked",G_CALLBACK(gtk_widget_destroy),RWin);

gtk_widget_show_all(RWin);
}
//----------------------------------------------------------------------------------------------------------------------
void Help(GtkWidget *W,gpointer Unused)
{
GtkWidget *Win,*Label;
 gchar Txt[1024];
 strncpy(Txt,
	 _("uhope: A Linux Shell for Microhope\n\n\
To use uhope:\n\
   1. Create, Edit and Save C-source (*.c) and Assembler (*.S and *.s) files just like gedit\n\
Sample files and the hardware manual are located in the folder microhope\n\
in the same location where uhope is installed\n\
   2. Compile C code by clicking Compile or Assembler code by clicking Assemble\n\
   3. You can view the objdump file (*.lst) by opening it in the editor\n\
   4. Connect Microhope and wait a minute\n\
   5. Click Detect-MH\n\
   6. If Microhope is not found, repeat or reconnect Microhope\n\
   7. Upload the hex file to Microhope by clicking Upload\n\
   8. After first connection, Upload may fail because Microhope is not ready\n\
   9. If Upload fails, click Microhope->Upload again\n"),
	 1024
	 );

 Win=gtk_dialog_new_with_buttons(_("Help"),GTK_WINDOW(MWin),GTK_DIALOG_DESTROY_WITH_PARENT,GTK_STOCK_OK,GTK_RESPONSE_NONE,NULL);
gtk_window_set_position(GTK_WINDOW(Win),GTK_WIN_POS_CENTER);
gtk_window_set_modal(GTK_WINDOW(Win),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(Win),GTK_WINDOW(MWin));
Label=gtk_label_new(Txt);
g_signal_connect_swapped(Win,"response",G_CALLBACK(gtk_widget_destroy),Win);
gtk_container_add(GTK_CONTAINER(GTK_DIALOG(Win)->vbox),Label);
gtk_widget_show_all(Win);
}
//----------------------------------------------------------------------------------------------------------------------
void Doc(GtkWidget * Unused0 ,gpointer Unused){
  g_spawn_command_line_async      ("microhope-doc", NULL);
}

//----------------------------------------------------------------------------------------------------------------------
void About(GtkWidget *W,gpointer Unused)
{
GtkWidget *Win,*Label;
 gchar Txt[1024];
strncpy(Txt,
	 _("uhope: A Linux Shell for Microhope\n\
Copyright (C) 2014  A.Chatterjee <DrAmbar@gmail.com>\n\n\
This program is free software: you can redistribute it and/or modify\n\
it under the terms of the GNU General Public License as published by\n\
the Free Software Foundation, either version 3 of the License, or\n\
(at your option) any later version.\n\n\
This program is distributed in the hope that it will be useful,\n\
but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\
GNU General Public License www.gnu.org/licenses\n\
for more details.\n"),
	 1024
	 );

 Win=gtk_dialog_new_with_buttons(_("About"),GTK_WINDOW(MWin),GTK_DIALOG_DESTROY_WITH_PARENT,GTK_STOCK_OK,GTK_RESPONSE_NONE,NULL);
gtk_window_set_position(GTK_WINDOW(Win),GTK_WIN_POS_CENTER);
gtk_window_set_modal(GTK_WINDOW(Win),TRUE);
gtk_window_set_transient_for(GTK_WINDOW(Win),GTK_WINDOW(MWin));
Label=gtk_label_new(Txt);
g_signal_connect_swapped(Win,"response",G_CALLBACK(gtk_widget_destroy),Win);
gtk_container_add(GTK_CONTAINER(GTK_DIALOG(Win)->vbox),Label);
gtk_widget_show_all(Win);
}
//----------------------------------------------------------------------------------------------------------------------
void ReallyQuit(GtkWidget *W,gint ResponseID,gpointer user_data)
{
if (ResponseID==GTK_RESPONSE_YES) gtk_main_quit();
else gtk_widget_destroy(W);
}
//----------------------------------------------------------------------------------------------------------------------
void Quit(GtkWidget *W,gpointer Unused)
{
GtkWidget *Win,*Label;

if (!UnsavedChanges) gtk_main_quit();
 Win=gtk_dialog_new_with_buttons(_("Quit"),NULL,GTK_DIALOG_MODAL,_("Dont quit"),GTK_RESPONSE_NO,GTK_STOCK_QUIT,
    GTK_RESPONSE_YES,NULL);
gtk_window_set_position(GTK_WINDOW(Win),GTK_WIN_POS_CENTER);
 Label=gtk_label_new(_("\nThere are unsaved changes.\nDo you really want to quit?\n"));
g_signal_connect(Win,"response",G_CALLBACK(ReallyQuit),NULL);
gtk_container_add(GTK_CONTAINER(GTK_DIALOG(Win)->vbox),Label);
gtk_widget_show_all(Win);
}
//----------------------------------------------------------------------------------------------------------------------
void FillUndo(int N)                                                       //Fills UBuf[N] (N=0,1) with the current text
{
GtkTextIter Start,End;
gchar *BufTxt;

gtk_text_buffer_get_start_iter(Buf,&Start); gtk_text_buffer_get_end_iter(Buf,&End);
BufTxt=gtk_text_buffer_get_text(Buf,&Start,&End,FALSE);
if (strlen(BufTxt)<MAX_FSIZE-1) strcpy(UBuf[N],BufTxt);
}
//----------------------------------------------------------------------------------------------------------------------
void Undo(GtkWidget *W,gpointer Unused)
{
MaskBufChg=TRUE;                                                                         //Ensure BufferChanged wont act
FillUndo(1-UStat);
gtk_text_buffer_set_text(Buf,UBuf[UStat],-1);
UStat=1-UStat;
MaskBufChg=FALSE;                                                                                    //Restore this flag
}
//----------------------------------------------------------------------------------------------------------------------
void BufferChanged(GtkWidget *W,gpointer Unused)
{
gchar *BufTxt;
GtkTextIter Start,End,EndSel;
GtkTextMark *Mark;
gint CurOfs;

UnsavedChanges=TRUE;
if (MaskBufChg) return;                                                 //Replace, Replace All or Undo is doing its work

Mark=gtk_text_buffer_get_mark(Buf,"selection_bound");    //Mark at end-of-selection (or cursor position if no selection)
gtk_text_buffer_get_iter_at_mark(Buf,&EndSel,Mark);                               //Iter at end-of-selection (or cursor)
gtk_text_buffer_get_start_iter(Buf,&Start);                                                     //Iter at start position
gtk_text_buffer_get_end_iter(Buf,&End);                                                           //Iter at end position
BufTxt=gtk_text_buffer_get_text(Buf,&Start,&EndSel,FALSE);             //Text from start to end-of-selection (or cursor)
CurOfs=strlen(BufTxt);                                                          //Offset to end-of-selection (or cursor)
if ((BufTxt[CurOfs-1] == 10 || BufTxt[CurOfs-1] == 32))                       //Last character typed is space or newline
   { FillUndo(1-UStat); Push=TRUE; }
else if (Push) { Push=FALSE; UStat=1-UStat; }
}
//----------------------------------------------------------------------------------------------------------------------
void CursorMoved(GtkWidget *W,gpointer Unused)
{
GtkTextIter Iter;
gint Row,Col;
gchar StatusLine[MAX_STAT];

gtk_text_buffer_get_iter_at_mark(Buf,&Iter,gtk_text_buffer_get_insert(Buf));
Row=gtk_text_iter_get_line(&Iter);
Col=gtk_text_iter_get_line_offset(&Iter);
gtk_statusbar_pop(GTK_STATUSBAR(StatBar),0);
 sprintf(StatusLine,_("%s \t Line:%d Col:%d"),FileName,Row,Col);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);
}
//----------------------------------------------------------------------------------------------------------------------
gboolean DeleteMain(GtkWidget *W,GdkEvent *Event,gpointer Data)
{
if (UnsavedChanges) { Quit(NULL,NULL); return TRUE; };
return FALSE;
}
//----------------------------------------------------------------------------------------------------------------------
static GtkActionEntry entries[25];
static guint n_entries=G_N_ELEMENTS(entries);

void initEntries(){ // calls to gettext are done at runtime
  entries[0]=(GtkActionEntry){"FileMenuAction",GTK_STOCK_FILE,_("_File")};
  entries[1]=(GtkActionEntry){"EditMenuAction",GTK_STOCK_EDIT,_("_Edit")};
  entries[2]=(GtkActionEntry){"HelpMenuAction",GTK_STOCK_EDIT,_("_Help")};
  entries[3]=(GtkActionEntry){"MicrohopeMenuAction",GTK_STOCK_EDIT,_("_Microhope")};

  entries[4]=(GtkActionEntry){"NewAction",GTK_STOCK_NEW,_("_New"),"<control>N",_("New"),G_CALLBACK(FileNew)};
  entries[5]=(GtkActionEntry){"OpenAction",GTK_STOCK_OPEN,_("_Open"),"<control>O",_("Open"),G_CALLBACK(FileOpen)};
  entries[6]=(GtkActionEntry){"SaveAction",GTK_STOCK_SAVE,_("_Save"),"<control>S",_("Save"),G_CALLBACK(FileSave)};
  entries[7]=(GtkActionEntry){"SaveAsAction",GTK_STOCK_SAVE_AS,_("Save _As"),"<shift><control>S",_("Save As"),G_CALLBACK(FileSaveAs)};
  entries[8]=(GtkActionEntry){"QuitAction",GTK_STOCK_QUIT,_("_Quit"),"<control>Q",_("Quit"),G_CALLBACK(Quit)};

  entries[9]=(GtkActionEntry){"UndoAction",GTK_STOCK_UNDO,_("_Undo"),"<control>Z",_("Undo"),G_CALLBACK(Undo)};
  entries[10]=(GtkActionEntry){"CutAction",GTK_STOCK_CUT,_("Cu_t"),"<control>X",_("Cut"),G_CALLBACK(EditCut)};
  entries[11]=(GtkActionEntry){"CopyAction",GTK_STOCK_COPY,_("_Copy"),"<control>C",_("Copy"),G_CALLBACK(EditCopy)};
  entries[12]=(GtkActionEntry){"PasteAction",GTK_STOCK_PASTE,_("_Paste"),"<control>V",_("Paste"),G_CALLBACK(EditPaste)};
  entries[13]=(GtkActionEntry){"DeleteAction",GTK_STOCK_DELETE,_("De_lete"),"Delete",_("Delete"),G_CALLBACK(EditDelete)};
  entries[14]=(GtkActionEntry){"FindAction",GTK_STOCK_FIND,_("Find"),"<control>F",_("Find"),G_CALLBACK(EditFind)};
  entries[15]=(GtkActionEntry){"FindNextAction",GTK_STOCK_FIND,_("Find Ne_xt"),"<control>G",_("Find Next"),G_CALLBACK(FindNext)};
  entries[16]=(GtkActionEntry){"ReplaceAction",GTK_STOCK_FIND_AND_REPLACE,_("_Replace"),"<control>H",_("Replace"),G_CALLBACK(EditReplace)};
  entries[17]=(GtkActionEntry){"SelectAllAction",GTK_STOCK_SELECT_ALL,_("SelectAll"),"<control>A",_("SelectAll"),G_CALLBACK(SelectAll)};

  entries[18]=(GtkActionEntry){"CompileAction",NULL,_("_Compile"),"",_("Compile"),G_CALLBACK(Compile)};
  entries[19]=(GtkActionEntry){"AssembleAction",NULL,_("_Assemble"),"",_("Assemble"),G_CALLBACK(Assemble)};
  entries[20]=(GtkActionEntry){"UploadAction",NULL,_("_Upload"),"",_("Upload"),G_CALLBACK(Upload)};
  entries[21]=(GtkActionEntry){"DetectHardwareAction",NULL,_("_Detect-MH"),"",_("Detect Microhope"),G_CALLBACK(DetectHardware)};

  entries[22]=(GtkActionEntry){"HelpAction",NULL,_("HowTo"),"",_("HowTo"),G_CALLBACK(Help)};
  entries[23]=(GtkActionEntry){"AboutAction",NULL,_("About"),"",_("About"),G_CALLBACK(About)};
  entries[24]=(GtkActionEntry){"DocAction",NULL,_("Documentation"),"",_("Documentation"),G_CALLBACK(Doc)};
}

//---------------------------------------------------------------------------------------------------------------------
void check_user_environment(gchar ** Path){
  gint res;
  gchar Str[MAX_FNAME+128];

  g_spawn_command_line_sync( "create-microhope-env",
			     NULL,
			     NULL,
			     &res,
			     NULL );
  if (res!=0){
    sprintf(Str,_("Could not create %s."), *Path);
    Attention(Str,FALSE);
    (void)getcwd(*Path,MAX_FNAME); //If directory does not exist, revert to current directory
  }
}

//----------------------------------------------------------------------------------------------------------------------
int main(int argc,char *argv[])
{
GtkWidget *VBox,*HBox,*SBox,*MenuBar,*Toolbar;
GtkActionGroup *ActionGroup;
GtkUIManager *MenuManager;
GError *Error;
struct stat Info;
gchar StatusLine[MAX_STAT],Str[MAX_FNAME+128];
char *HomeStr;
static gchar GuiStr[]="\
   <ui>\
     <menubar name='MainMenu'>\
        <menu name='FileMenu' action='FileMenuAction'>\
           <menuitem name='New' action='NewAction' always-show-image='true'/>\
           <menuitem name='Open' action='OpenAction' always-show-image='true'/>\
           <menuitem name='Save' action='SaveAction' always-show-image='true'/>\
           <menuitem name='Save As' action='SaveAsAction' always-show-image='true'/>\
           <separator/>\
           <menuitem name='Quit' action='QuitAction' always-show-image='true'/>\
        </menu>\
        <menu name='EditMenu' action='EditMenuAction'>\
           <menuitem name='Undo' action='UndoAction' always-show-image='true'/><separator/>\
           <menuitem name='Cut' action='CutAction' always-show-image='true'/>\
           <menuitem name='Copy' action='CopyAction' always-show-image='true'/>\
           <menuitem name='Paste' action='PasteAction' always-show-image='true'/>\
           <menuitem name='Delete' action='DeleteAction' always-show-image='true'/><separator/>\
           <menuitem name='Find' action='FindAction' always-show-image='true'/>\
           <menuitem name='FindNext' action='FindNextAction' always-show-image='true'/>\
           <menuitem name='Replace' action='ReplaceAction' always-show-image='true'/>\
           <separator/>\
           <menuitem name='SelectAll' action='SelectAllAction' always-show-image='true'/>\
        </menu>\
        <menu name='HelpMenu' action='HelpMenuAction'>\
           <menuitem name='About' action='AboutAction' always-show-image='true'/><separator/>\
           <menuitem name='HowTo' action='HelpAction' always-show-image='true'/>\
           <menuitem name='Doc' action='DocAction' always-show-image='true'/>\
        </menu>\
     </menubar>\
     <toolbar name='MainToolbar' action='MainMenuBarAction'>\
       <placeholder name='ToolItems'>\
         <toolitem name='Compile' action='CompileAction'/>\
         <toolitem name='Assemble' action='AssembleAction'/>\
         <toolitem name='Upload' action='UploadAction'/>\
         <toolitem name='DetectHardware' action='DetectHardwareAction'/>\
       </placeholder>\
     </toolbar>\
   </ui>";

 setlocale (LC_ALL, "");
 bindtextdomain(GETTEXT_PACKAGE, "/usr/share/locale");
 textdomain(GETTEXT_PACKAGE);
 bind_textdomain_codeset(GETTEXT_PACKAGE, "UTF-8");

gtk_init(&argc,&argv);
MWin=gtk_window_new(GTK_WINDOW_TOPLEVEL);

g_signal_connect(MWin,"delete_event",G_CALLBACK(DeleteMain),NULL);
g_signal_connect(MWin,"destroy",G_CALLBACK(gtk_main_quit),NULL);

 gtk_window_set_title(GTK_WINDOW(MWin),_("uhope - A Linux Shell for Microhope"));
gtk_window_set_default_size(GTK_WINDOW(MWin),920,470);
gtk_window_set_position(GTK_WINDOW(MWin),GTK_WIN_POS_CENTER);
 
VBox=gtk_vbox_new(FALSE,1);
gtk_container_set_border_width(GTK_CONTAINER(VBox),1);
gtk_container_add(GTK_CONTAINER(MWin),VBox);
HBox=gtk_hbox_new(FALSE,0);
gtk_box_pack_start(GTK_BOX(VBox),HBox,FALSE,TRUE,0);

ActionGroup=gtk_action_group_new("GuiActions");
gtk_action_group_set_translation_domain(ActionGroup,"blah");
MenuManager=gtk_ui_manager_new();
 initEntries();
 gtk_action_group_add_actions(ActionGroup,entries,n_entries,NULL);
gtk_ui_manager_insert_action_group(MenuManager,ActionGroup,0);

Error=NULL;
gtk_ui_manager_add_ui_from_string(MenuManager,GuiStr,-1,&Error);
 if (Error) { Attention(_("Building menus failed"),FALSE); g_error_free(Error); }

MenuBar=gtk_ui_manager_get_widget(MenuManager,"/MainMenu");
gtk_box_pack_start(GTK_BOX(HBox),MenuBar,FALSE,FALSE,0);
Toolbar=gtk_ui_manager_get_widget(MenuManager,"/MainToolbar");
gtk_toolbar_set_style(GTK_TOOLBAR(Toolbar),GTK_TOOLBAR_TEXT);
gtk_box_pack_start(GTK_BOX(HBox),Toolbar,TRUE,TRUE,0);
gtk_window_add_accel_group(GTK_WINDOW(MWin),gtk_ui_manager_get_accel_group(MenuManager));

SBox=gtk_scrolled_window_new(NULL,NULL);
gtk_container_set_border_width(GTK_CONTAINER(SBox),2);
gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(SBox),GTK_POLICY_AUTOMATIC,GTK_POLICY_AUTOMATIC);
gtk_box_pack_start(GTK_BOX(VBox),SBox,TRUE,TRUE,0);

TextView=gtk_text_view_new();
gtk_container_add(GTK_CONTAINER(SBox),TextView);
Buf=gtk_text_view_get_buffer(GTK_TEXT_VIEW(TextView));
gtk_text_buffer_set_text(Buf,"",-1);
g_signal_connect(Buf,"changed",G_CALLBACK(BufferChanged),NULL);
g_signal_connect(Buf,"mark_set",G_CALLBACK(CursorMoved),NULL);

StatBar=gtk_statusbar_new();
gtk_box_pack_start(GTK_BOX(VBox),StatBar,FALSE,TRUE,0);
StatID=gtk_statusbar_get_context_id(GTK_STATUSBAR(StatBar),"StatBar");
strcpy(StatusLine,FileName);
gtk_statusbar_push(GTK_STATUSBAR(StatBar),StatID,StatusLine);

gtk_widget_show_all(MWin);

HomeStr=getenv("HOME");
sprintf(Path,"%s/microhope",HomeStr);
if (stat(Path,&Info)){
  gtk_timeout_add(1,check_user_environment,&Path);
 }
gtk_main();
return 0;
}
//----------------------------------------------------------------------------------------------------------------------
