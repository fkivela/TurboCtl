Search.setIndex({docnames:["index","modules/index","modules/telegram/api","modules/telegram/codes","modules/telegram/datatypes","modules/telegram/index","modules/telegram/parser","modules/telegram/telegram","modules/ui/advanced_tui","modules/ui/command_line_ui","modules/ui/control_interface","modules/ui/index","modules/ui/queuefile","modules/ui/status_format","modules/ui/table","modules/ui/widgets","modules/virtualpump/hardware_component","modules/virtualpump/index","modules/virtualpump/parameter_component","modules/virtualpump/virtualconnection","modules/virtualpump/virtualpump"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":2,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["index.rst","modules/index.rst","modules/telegram/api.rst","modules/telegram/codes.rst","modules/telegram/datatypes.rst","modules/telegram/index.rst","modules/telegram/parser.rst","modules/telegram/telegram.rst","modules/ui/advanced_tui.rst","modules/ui/command_line_ui.rst","modules/ui/control_interface.rst","modules/ui/index.rst","modules/ui/queuefile.rst","modules/ui/status_format.rst","modules/ui/table.rst","modules/ui/widgets.rst","modules/virtualpump/hardware_component.rst","modules/virtualpump/index.rst","modules/virtualpump/parameter_component.rst","modules/virtualpump/virtualconnection.rst","modules/virtualpump/virtualpump.rst"],objects:{"turboctl.telegram":{api:[2,0,0,"-"],codes:[3,0,0,"-"],datatypes:[4,0,0,"-"],parser:[6,0,0,"-"],telegram:[7,0,0,"-"]},"turboctl.telegram.api":{read_parameter:[2,1,1,""],send:[2,1,1,""],status:[2,1,1,""],write_parameter:[2,1,1,""]},"turboctl.telegram.codes":{AccessError:[3,2,1,""],CannotChangeError:[3,2,1,""],ControlBits:[3,3,1,""],CustomInt:[3,3,1,""],FlagBits:[3,3,1,""],MinMaxError:[3,2,1,""],OtherError:[3,2,1,""],ParameterAccess:[3,3,1,""],ParameterCode:[3,3,1,""],ParameterError:[3,3,1,""],ParameterException:[3,2,1,""],ParameterExceptionMeta:[3,3,1,""],ParameterIndexError:[3,2,1,""],ParameterResponse:[3,3,1,""],SavingError:[3,2,1,""],StatusBits:[3,3,1,""],WrongNumError:[3,2,1,""],get_parameter_code:[3,1,1,""],get_parameter_mode:[3,1,1,""]},"turboctl.telegram.codes.CustomInt":{__new__:[3,4,1,""]},"turboctl.telegram.codes.ParameterException":{member:[3,4,1,""]},"turboctl.telegram.codes.ParameterExceptionMeta":{member:[3,4,1,""]},"turboctl.telegram.datatypes":{BYTESIZE:[4,5,1,""],Bin:[4,3,1,""],Data:[4,3,1,""],Float:[4,3,1,""],Sint:[4,3,1,""],Uint:[4,3,1,""],maxsint:[4,1,1,""],maxuint:[4,1,1,""],minsint:[4,1,1,""]},"turboctl.telegram.datatypes.Bin":{__bytes__:[4,4,1,""],__init__:[4,4,1,""]},"turboctl.telegram.datatypes.Data":{__add__:[4,4,1,""],__eq__:[4,4,1,""],__getitem__:[4,4,1,""],__repr__:[4,4,1,""],bits:[4,4,1,""],n_bytes:[4,4,1,""],value:[4,4,1,""]},"turboctl.telegram.datatypes.Float":{__add__:[4,4,1,""],__bytes__:[4,4,1,""],__getitem__:[4,4,1,""],__init__:[4,4,1,""]},"turboctl.telegram.datatypes.Sint":{__bytes__:[4,4,1,""],__init__:[4,4,1,""]},"turboctl.telegram.datatypes.Uint":{__bytes__:[4,4,1,""],__init__:[4,4,1,""]},"turboctl.telegram.parser":{ERRORS:[6,6,1,""],ErrorOrWarning:[6,3,1,""],PARAMETERS:[6,6,1,""],Parameter:[6,3,1,""],WARNINGS:[6,6,1,""],load_errors:[6,1,1,""],load_parameters:[6,1,1,""],load_warnings:[6,1,1,""],main:[6,1,1,""]},"turboctl.telegram.parser.ErrorOrWarning":{fields:[6,4,1,""],name:[6,6,1,""],number:[6,6,1,""],possible_cause:[6,6,1,""],remedy:[6,6,1,""]},"turboctl.telegram.parser.Parameter":{"default":[6,6,1,""],bits:[6,6,1,""],datatype:[6,6,1,""],description:[6,6,1,""],fields:[6,4,1,""],indices:[6,6,1,""],max_value:[6,6,1,""],min_value:[6,6,1,""],name:[6,6,1,""],number:[6,6,1,""],unit:[6,6,1,""],writable:[6,6,1,""]},"turboctl.telegram.telegram":{Telegram:[7,3,1,""],TelegramBuilder:[7,3,1,""],TelegramReader:[7,3,1,""],checksum:[7,1,1,""]},"turboctl.telegram.telegram.Telegram":{LENGTH:[7,6,1,""],__bytes__:[7,4,1,""],current:[7,6,1,""],flag_bits:[7,6,1,""],frequency:[7,6,1,""],parameter_code:[7,6,1,""],parameter_index:[7,6,1,""],parameter_number:[7,6,1,""],parameter_value:[7,6,1,""],temperature:[7,6,1,""],voltage:[7,6,1,""]},"turboctl.telegram.telegram.TelegramBuilder":{__init__:[7,4,1,""],build:[7,4,1,""],from_bytes:[7,4,1,""],parameters:[7,6,1,""],set_current:[7,4,1,""],set_flag_bits:[7,4,1,""],set_frequency:[7,4,1,""],set_parameter_index:[7,4,1,""],set_parameter_mode:[7,4,1,""],set_parameter_number:[7,4,1,""],set_parameter_value:[7,4,1,""],set_temperature:[7,4,1,""],set_voltage:[7,4,1,""]},"turboctl.telegram.telegram.TelegramReader":{__init__:[7,4,1,""],__repr__:[7,4,1,""],__str__:[7,4,1,""],current:[7,4,1,""],flag_bits:[7,4,1,""],frequency:[7,4,1,""],parameter_error:[7,4,1,""],parameter_index:[7,4,1,""],parameter_mode:[7,4,1,""],parameter_number:[7,4,1,""],parameter_value:[7,4,1,""],telegram:[7,6,1,""],temperature:[7,4,1,""],type:[7,6,1,""],voltage:[7,4,1,""]},"turboctl.ui":{advanced_tui:[8,0,0,"-"],command_line_ui:[9,0,0,"-"],control_interface:[10,0,0,"-"],queuefile:[12,0,0,"-"],status_format:[13,0,0,"-"],table:[14,0,0,"-"],widgets:[15,0,0,"-"]},"turboctl.ui.advanced_tui":{AdvancedTUI:[8,3,1,""]},"turboctl.ui.advanced_tui.AdvancedTUI":{__init__:[8,4,1,""],command_line_interface:[8,6,1,""],display:[8,6,1,""],run:[8,4,1,""]},"turboctl.ui.command_line_ui":{CommandLineUI:[9,3,1,""]},"turboctl.ui.command_line_ui.CommandLineUI":{__enter__:[9,4,1,""],__exit__:[9,4,1,""],__init__:[9,4,1,""],cmd_debug:[9,4,1,""],cmd_exit:[9,4,1,""],cmd_help:[9,4,1,""],cmd_info:[9,4,1,""],cmd_list:[9,4,1,""],cmd_pump:[9,4,1,""],cmd_read:[9,4,1,""],cmd_status:[9,4,1,""],cmd_write:[9,4,1,""],cmds_and_aliases:[9,6,1,""],control_interface:[9,6,1,""],debug:[9,6,1,""],indent:[9,6,1,""],input:[9,4,1,""],inputfile:[9,6,1,""],intro:[9,6,1,""],outputfile:[9,6,1,""],print:[9,4,1,""],prompt:[9,6,1,""],run:[9,4,1,""]},"turboctl.ui.control_interface":{ControlInterface:[10,3,1,""],SERIAL_KWARGS:[10,5,1,""],Status:[10,3,1,""]},"turboctl.ui.control_interface.ControlInterface":{__enter__:[10,4,1,""],__exit__:[10,4,1,""],__init__:[10,4,1,""],close:[10,4,1,""],get_status:[10,4,1,""],pump_off:[10,4,1,""],pump_on:[10,4,1,""],read_parameter:[10,4,1,""],status:[10,6,1,""],timestep:[10,6,1,""],write_parameter:[10,4,1,""]},"turboctl.ui.control_interface.Status":{__setattr__:[10,4,1,""],callback:[10,6,1,""],current:[10,6,1,""],frequency:[10,6,1,""],pump_on:[10,6,1,""],status_bits:[10,6,1,""],temperature:[10,6,1,""],voltage:[10,6,1,""]},"turboctl.ui.queuefile":{QueueFile:[12,3,1,""]},"turboctl.ui.queuefile.QueueFile":{__init__:[12,4,1,""],block:[12,6,1,""],flush:[12,4,1,""],queue:[12,6,1,""],read:[12,4,1,""],readline:[12,4,1,""],write:[12,4,1,""]},"turboctl.ui.status_format":{green_button:[13,6,1,""],palette:[13,6,1,""],red_button:[13,6,1,""],status_screen:[13,1,1,""]},"turboctl.ui.table":{array:[14,1,1,""],table:[14,1,1,""]},"turboctl.ui.widgets":{CommandHistory:[15,3,1,""],CommandLines:[15,3,1,""],Position:[15,3,1,""],ScrollBar:[15,3,1,""],ScrollButton:[15,3,1,""],ScrollableCommandLines:[15,3,1,""],Scroller:[15,3,1,""]},"turboctl.ui.widgets.CommandHistory":{__init__:[15,4,1,""],down:[15,4,1,""],enter_command:[15,4,1,""],get_command:[15,4,1,""],history:[15,6,1,""],index:[15,6,1,""],temp_history:[15,6,1,""],up:[15,4,1,""],update_command:[15,4,1,""]},"turboctl.ui.widgets.CommandLines":{__init__:[15,4,1,""],edit:[15,6,1,""],enter:[15,4,1,""],history:[15,6,1,""],history_down:[15,4,1,""],history_up:[15,4,1,""],inputfile:[15,6,1,""],keypress:[15,4,1,""],move_cursor_to_end:[15,4,1,""],outputfile:[15,6,1,""],update:[15,4,1,""]},"turboctl.ui.widgets.Position":{__init__:[15,4,1,""],absolute:[15,6,1,""],listeners:[15,6,1,""],max_absolute:[15,4,1,""],relative:[15,6,1,""],total_rows:[15,6,1,""],visible_rows:[15,6,1,""]},"turboctl.ui.widgets.ScrollBar":{__init__:[15,4,1,""],background_char:[15,6,1,""],mouse_event:[15,4,1,""],position:[15,6,1,""],render:[15,4,1,""],scroller_char:[15,6,1,""]},"turboctl.ui.widgets.ScrollButton":{__init__:[15,4,1,""],mouse_event:[15,4,1,""],position:[15,6,1,""],step:[15,6,1,""]},"turboctl.ui.widgets.ScrollableCommandLines":{__init__:[15,4,1,""],arrow_down:[15,6,1,""],arrow_up:[15,6,1,""],command_lines:[15,6,1,""],position:[15,6,1,""],scrollbar:[15,6,1,""],scroller:[15,6,1,""]},"turboctl.ui.widgets.Scroller":{__init__:[15,4,1,""],keypress:[15,4,1,""],mouse_event:[15,4,1,""],position:[15,6,1,""],render:[15,4,1,""],widget:[15,6,1,""]},"turboctl.virtualpump":{hardware_component:[16,0,0,"-"],parameter_component:[18,0,0,"-"],virtualconnection:[19,0,0,"-"],virtualpump:[20,0,0,"-"]},"turboctl.virtualpump.hardware_component":{HWParameters:[16,3,1,""],HardwareComponent:[16,3,1,""],Variables:[16,3,1,""]},"turboctl.virtualpump.hardware_component.HWParameters":{__init__:[16,4,1,""],current:[16,6,1,""],error_counter:[16,6,1,""],error_frequency_list:[16,6,1,""],error_hour_list:[16,6,1,""],error_list:[16,6,1,""],frequency:[16,6,1,""],frequency_setpoint:[16,6,1,""],motor_power:[16,6,1,""],motor_temperature:[16,6,1,""],operating_hours:[16,6,1,""],overload_error_counter:[16,6,1,""],power_failure_error_counter:[16,6,1,""],save_data:[16,6,1,""],temperature:[16,6,1,""],voltage:[16,6,1,""],warning_list:[16,6,1,""]},"turboctl.virtualpump.hardware_component.HardwareComponent":{CURRENT:[16,6,1,""],TEMPERATURE:[16,6,1,""],VOLTAGE:[16,6,1,""],__init__:[16,4,1,""],abs_acceleration:[16,6,1,""],frequency:[16,6,1,""],handle_hardware:[16,4,1,""],is_on:[16,6,1,""],off:[16,4,1,""],on:[16,4,1,""],step:[16,6,1,""],stop:[16,4,1,""],variables:[16,6,1,""]},"turboctl.virtualpump.hardware_component.Variables":{__getattr__:[16,4,1,""],__init__:[16,4,1,""],__setattr__:[16,4,1,""],parameters:[16,6,1,""]},"turboctl.virtualpump.parameter_component":{ExtendedParameter:[18,3,1,""],ExtendedParameters:[18,3,1,""],ParameterComponent:[18,3,1,""]},"turboctl.virtualpump.parameter_component.ExtendedParameter":{"default":[18,6,1,""],__init__:[18,4,1,""],__str__:[18,4,1,""],bits:[18,6,1,""],datatype:[18,6,1,""],indices:[18,6,1,""],max_value:[18,4,1,""],min_value:[18,4,1,""],number:[18,6,1,""],parameters:[18,6,1,""],value:[18,6,1,""],writable:[18,6,1,""]},"turboctl.virtualpump.parameter_component.ExtendedParameters":{__init__:[18,4,1,""]},"turboctl.virtualpump.parameter_component.ParameterComponent":{__init__:[18,4,1,""],handle_parameter:[18,4,1,""],parameters:[18,6,1,""]},"turboctl.virtualpump.virtualconnection":{VirtualConnection:[19,3,1,""]},"turboctl.virtualpump.virtualconnection.VirtualConnection":{__enter__:[19,4,1,""],__exit__:[19,4,1,""],__init__:[19,4,1,""],buffer_size:[19,6,1,""],close:[19,4,1,""],close_all:[19,4,1,""],default_process:[19,4,1,""],is_running:[19,4,1,""],port:[19,4,1,""],process:[19,6,1,""],running_instances:[19,6,1,""],sleep_time:[19,6,1,""],thread:[19,6,1,""],user_end:[19,6,1,""],virtual_end:[19,6,1,""]},"turboctl.virtualpump.virtualpump":{VirtualPump:[20,3,1,""]},"turboctl.virtualpump.virtualpump.VirtualPump":{__enter__:[20,4,1,""],__exit__:[20,4,1,""],__init__:[20,4,1,""],connection:[20,6,1,""],hardware_component:[20,6,1,""],parameter_component:[20,6,1,""],process:[20,4,1,""],stop:[20,4,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","exception","Python exception"],"3":["py","class","Python class"],"4":["py","method","Python method"],"5":["py","data","Python data"],"6":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:function","2":"py:exception","3":"py:class","4":"py:method","5":"py:data","6":"py:attribute"},terms:{"boolean":10,"break":9,"byte":[4,7,19,20],"case":[4,6,7,16,18,19],"catch":[3,9],"class":[3,4,6,7,8,9,10,12,14,15,16,18,19,20],"default":[6,7,9,10,18,19],"enum":[3,7],"final":8,"float":[4,10,15,16,19],"function":[2,3,5,6,7,9,10,14,15,16,17,19,20],"import":6,"int":[3,4,6,7,10,14,15,18,19],"kivel\u00e4":0,"long":19,"new":[4,7,8,9,10,12,15,16,18,19,20],"public":0,"return":[2,3,4,6,7,9,10,12,13,14,15,16,18,19,20],"short":3,"static":[3,19],"true":[2,3,4,9,10,12,15,19],"try":[3,7,8],"while":[3,15,18],FOR:0,For:16,Its:[10,19],The:[0,1,2,3,4,6,7,8,9,10,12,13,14,15,16,18,19,20],These:9,Use:8,With:7,__add__:4,__bytes__:[4,7],__enter__:[9,10,19,20],__eq__:4,__exit__:[9,10,19,20],__getattr__:16,__getattribute__:16,__getitem__:4,__init__:[4,6,7,8,9,10,12,15,16,18,19,20],__new__:3,__repr__:[4,6,7],__setattr__:[10,16],__str__:[6,7,18],about:[2,6,9,10],abov:[7,15,16],abs_acceler:16,absolut:15,acceler:16,accept:[3,4,9],access:[3,7,16,17,18,19,20],accesserror:3,accord:7,accordingli:[10,16],activ:9,actual:[7,16,17,18,19,20],add:[7,15],added:[2,7],addit:0,address:7,adr:7,advanced_tui:[0,1,11],advancedtui:[8,13],affect:[6,7,10,16],after:[7,9,18,19],again:[9,19],algorithm:[7,9],alia:9,alias:9,all:[2,3,4,7,9,10,12,14,15,16,18,19],allow:16,along:0,alongsid:3,also:[0,2,3,6,7,9,10,15,19],alwai:[3,4,7,12,15,16,18],among:15,amount:[15,16],analog:16,ani:[0,3,4,7,9,15,16,20],anoth:[6,9,15,18],api:[0,1,5],append:4,appli:16,approxim:15,aren:7,arg:3,argument:[2,3,4,7,9,10,12,15,19],arrai:14,arrow:15,arrow_down:15,arrow_up:15,ask:[9,10],assign:[3,7,18,19],associ:7,attribut:[3,6,7,9,10,14,15,16,18,19],attributeerror:[3,12],auto_upd:[9,10],automat:[0,6,7,8,10,15,16,19],avoid:18,back:[2,10,18,20],background:9,background_char:15,bar:15,base:[3,4,7,8,15,18,19],basescreen:8,baudrat:10,bcc:7,beak:8,becaus:[3,4,7,9,16,18],been:[3,8,15],befor:19,begin:[19,20],behav:18,behaviour:[6,12,15,20],being:[3,15],below:[7,8,15,16],between:[10,12,15,16],bin:[4,6,7],binari:4,bit:[2,3,4,6,7,16,18,19],block:[3,7,8,9,10,12,19,20],bool:[6,9,10,12,16],both:[2,3,7,10,16,18],bottom:15,bound:10,box:15,brows:15,buffer:19,buffer_s:19,build:[7,16],built:[3,7,8,9,16],button:15,byte_:7,bytes:[4,10],bytes_:7,bytes_in:20,call:[4,6,7,8,9,10,15,16,19,20],callabl:[8,10],callback:10,can:[0,2,3,4,6,7,9,10,12,14,15,16,17,18,19,20],cannot:[2,3,4,6,7,9,16,18,20],cannotchangeerror:3,canva:15,caught:9,caus:[2,6,16],celsiu:6,chang:[3,6,7,8,10,15,16,18,20],charact:[3,4,12,15],check:[7,19],checksum:7,circl:13,circuit:[7,10,16],circular:3,circumv:3,classmethod:19,classnam:[4,7],click:15,close:[8,9,10,19,20],close_al:19,cls:3,cmd_:9,cmd_debug:9,cmd_exampl:9,cmd_exit:9,cmd_help:9,cmd_info:9,cmd_list:9,cmd_pump:9,cmd_read:9,cmd_statu:9,cmd_write:9,cmds_and_alias:9,code:[0,1,5,7,8,16,19],col:15,collect:16,colour:13,column:14,combin:[4,8],command:[2,7,8,9,10,15,16,18,19,20],command_lin:15,command_line_interfac:8,command_line_ui:[0,1,11],commandhistori:15,commandlin:15,commandlineui:[8,9],common:2,commun:[5,7,8,19],complement:4,compon:16,compos:4,comput:[3,7],condit:[3,6,7,10,16],connect:[2,10,19,20],consecut:15,consist:[7,15],constant:16,construct:[7,18],consum:9,contact:0,contain:[0,1,2,3,4,5,6,7,9,11,12,15,16,17],content:[7,8,10,13,20],continu:[9,19],control:[0,2,3,7,8,9,12,13,16],control_interfac:[0,1,9,11],controlbit:[3,7,16],controlinterfac:[9,10],convent:7,convert:[7,10,16],copi:[0,7,18],copyright:0,correct:3,correctli:16,correspond:[0,3,6,7,9,14,16,18],count:[15,16],crash:[8,9],creat:[3,5,6,7,9,10,12,14,15,19],cumbersom:7,current:[6,7,10,15,16,18,19],cursor:15,custom:[3,7],customint:3,cut:16,data:[2,4,6,7,16,18,19,20],databas:14,dataclass:[6,7],datatyp:[0,1,5,6,7,16,18],deactiv:9,debug:9,deceler:16,decreas:15,default_process:19,defin:[2,3,4,6,7,8,9,10,12,15,16,18],degre:6,del:19,denot:7,depend:[3,6,7,9,18],describ:[3,6,9,18],descript:[3,6,16],descriptor:19,detail:[0,4,7,9],determin:[7,10],dev:[10,19],develop:0,devic:[10,19],dict:[6,7,14,16,18],dictionari:6,differ:[3,4,6,7,12,15],direct:3,directli:[4,7],directori:6,disabl:9,displai:[8,9,13,14,15,18],distribut:0,disturb:16,divid:[1,4],docstr:[9,15],document:8,doe:12,doesn:[3,7,9,19],doing:19,done:15,down:15,draw:15,due:2,dummi:16,dure:9,each:[3,7,9,14,15,16,18],easier:[9,12],easiest:3,easili:[3,7,9,12],edg:15,edit:[9,15],effect:15,either:0,empti:[2,4,10,14,15,20],emul:[12,15],enabl:[7,20],encapsul:16,encount:12,end:[4,7,8,9,15,19],enter:[8,9,10,15],enter_command:15,entri:[7,8,15],enumnam:3,equal:[4,15],error:[2,3,6,7,9,14,16,18],error_count:16,error_frequency_list:16,error_hour_list:16,error_list:16,errororwarn:[6,14],etc:15,eval:7,evalu:[2,7],even:[0,7,16,18],event:15,everi:[9,10,16],exact:[7,16],exactli:[3,4],exampl:[4,7,8,9,18],exc_typ:10,exc_valu:10,except:[3,4],exception_typ:9,exception_valu:9,exclud:7,exclus:7,execut:[6,8,9],exist:[3,4,7,9,12],exit:[8,9,10,19,20],expand:16,explain:[6,13,15],explicitli:[7,10],express:4,extend:18,extended_paramet:18,extendedparamet:[16,18],factori:10,fail:7,fals:[2,3,4,9,10,12,15,19],far:15,fast:16,felik:0,field:[3,6,8,14,16],file:[6,8,9,12,15,19],filenam:6,filenotfounderror:6,find:16,first:[3,7],firstnam:0,fit:0,fix:15,flag:[10,12,16],flag_bit:7,flagbit:3,flow:15,flush:[9,12],focu:15,follow:[0,1,2,3,4,7,9,16,18,19],form:[4,9,10,15,19,20],format:[4,7,8,13,14,18],found:[6,16,18],foundat:0,four:9,free:[0,19],freez:16,frequenc:[7,10,16],frequency_setpoint:16,friendli:7,from:[3,6,7,8,9,12,15,16,18,19,20],from_byt:7,full:4,fusor:0,futur:16,gener:[0,6,7,15],get:[4,9],get_command:15,get_parameter_cod:3,get_parameter_mod:3,get_statu:10,give:[3,4,9,15,16],given:[4,7,9,10,12,15,16,19],gnu:0,gradual:16,green:13,green_button:13,group:3,handl:[15,16,18,19,20],handle_hardwar:16,handle_paramet:[16,18],happen:12,hardwar:[16,20],hardware_compon:[0,1,17,20],hardwarecompon:[16,20],has:[0,3,6,7,9,15,16,18,19],hasn:8,have:[0,2,3,4,6,7,10,16,19],height:15,help:9,helsinki:0,here:[7,13,15,19],histori:15,history_down:15,history_up:15,hold:[6,18],hope:0,hour:16,how:[4,7,13,15,16,19],howev:[3,7,16],http:0,human:[7,9],hvctl:0,hwparamet:16,ident:15,ieee:4,ignor:[9,10,16],immut:18,impli:0,includ:[7,9,12,15,16],incom:20,increas:15,ind:7,indent:9,index:[2,3,4,6,7,9,10,15,16],indic:[6,7,12,16,18],infinit:14,info:9,inform:[8,9,10],inherit:3,initi:[3,4,7,8,9,10,13,15,16,18,19,20],input:[8,9,12,15,16,19],input_:19,inputfil:[8,9,15],ins:7,instal:8,instanc:[2,3,4,7,9,10,16,18,19],instead:[3,4,6,7,8,9,13,14,15,16,19],integ:[4,16],intend:0,interfac:[8,9,11,12,15],intermedi:[7,10,16],intern:0,interpret:[7,13,19,20],intial:12,intro:9,invalid:[2,3,4,7,9,10],invis:15,is_on:16,is_run:19,isn:[3,6,7,9,10,14],issu:8,iter:[7,8,9,13,15,16],its:[3,6,7,8,9,12,15,19,20],itself:3,just:7,keep:[10,15,16],kei:[4,6,7,14,15,18],keyerror:18,keypress:15,keyword:10,kwarg:3,lack:[3,4],largest:4,lastnam:0,later:[0,15],latest:15,least:16,left:[8,15],len:4,length:[4,7,15,18],less:[4,9,12],letter:9,leybold:[0,7],lge:7,librari:15,like:[3,4,6,8,9,12,15,18,19],likewis:4,line:[6,8,9,15],linux:[0,15],list:[6,7,9,10,14,15,16,18],listen:15,load_error:6,load_paramet:6,load_warn:6,locat:[0,6,8,15,16],lock:16,longer:9,loop:[8,9],lost:16,machin:19,made:15,mai:[4,7,8,9,15],main:[6,8],mainloop:8,make:[3,8,9,12,15,16,20],mani:[4,19],manner:19,manual:[7,18],match:[3,4,16],max_absolut:15,max_valu:[6,18],maximum:[6,14,15,18],maxsint:4,maxuint:4,mean:[3,6,7],meant:[3,4,19],member:[3,7,10],member_nam:3,member_valu:3,memori:[3,15,16],merchant:0,messag:[3,7,9],metaclass:3,method:[3,4,6,7,8,9,10,12,16,19],min_valu:[6,18],minimum:[6,18],minmaxerror:3,minsint:4,minumum:6,mirror:0,mode:[3,7,9],modifi:[0,15,16],modul:[0,2,3,4,6,7,8,9,12,13,14,15,16,18,19,20],modulenam:0,more:[0,4,7],most:[0,4,16,18,19],motor:[7,10,16],motor_pow:16,motor_temperatur:16,mous:15,mouse_ev:15,move:[15,16],move_cursor_to_end:15,multipl:[3,6,15],multipli:4,must:[3,4,7,10],n_byte:4,name:[6,7,9,10,14,16,19],nan:4,need:[3,4,9,16,18],neg:[4,7,15],nest:13,never:12,newer:15,newest:15,newlin:12,node:7,non:[3,4,7,18],none:[4,6,7,9,10,12,15,19],nonvolatil:[3,16],normal:[7,9,16],note:[7,10,16],noth:[12,15],number:[2,3,4,6,7,9,10,12,14,15,16,18],object:[3,4,6,7,8,9,10,12,13,14,15,16,18,19,20],occur:16,off:[2,9,10,16],often:3,old:15,older:15,oldest:[15,16],onc:19,one:[3,7,10,12,15],ones:15,onli:[3,4,7,9,10,15,16,18,19],open:9,openpti:12,oper:[0,7,9,16],operating_hour:16,option:[0,4],order:[3,6,9,16,18],ordereddict:6,org:0,origin:[15,18],other:[3,4,7,15,16,18,19],othererror:3,otherwis:[2,3,4,7,9,10,15,16,19],out:16,output:[8,9,12,15,19],outputfil:[8,9,15],outsid:3,overload:16,overload_error_count:16,overrid:7,p18:[6,18],packag:[0,1,20],pad:4,palett:[8,13],parallel:[8,9,10,16,19,20],param_channel:16,paramet:[2,3,4,6,7,8,9,10,13,14,15,16,18,19,20],parameter_cod:7,parameter_compon:[0,1,17,20],parameter_error:7,parameter_index:7,parameter_mod:7,parameter_nam:16,parameter_numb:7,parameter_valu:7,parameteraccess:3,parametercod:3,parametercompon:[16,18,20],parametererror:[3,7],parametererrorx:3,parameterexcept:3,parameterexceptionmeta:3,parameterindexerror:3,parameterrespons:3,pariti:[7,10],pars:[6,9],parser:[0,1,5],part:[12,15,16,18],particular:0,pass:[3,7,8,9,10,15,16],path:6,pattern:9,perform:20,permit:7,physic:20,pke:7,plain:9,point:[4,15],poll:9,port:[7,9,10,19],portion:15,posit:[4,15,16],possibl:[3,6,12,16,19,20],possible_caus:6,power:[7,16],power_failure_error_count:16,precis:4,present:[3,8,13,16],press:15,prevent:[3,8,9,16],previou:15,previous:15,print:[8,9,12,14,15],probabl:8,problem:3,process:[19,20],process_channel:16,program:[0,3,8,9,11,12,17,20],prompt:9,properli:3,properti:[3,4,6,7,15,16,18,19],protocol:7,provid:[9,15],pts:19,pty:12,publish:0,pump:[0,2,3,5,6,7,9,10,13,16,17,18,20],pump_off:10,pump_on:[2,10],purpos:[0,6,7,16],pwe:7,python:[0,3,7,16,19],pzd1:7,pzd2:7,pzd3:7,pzd4:7,pzd6:7,queri:[2,3,7,10,16,18],queue:12,queuefil:[0,1,11],race:16,rais:[2,3,4,6,7,9,10,12,14,18],rang:[3,4,6],rate:16,read:[2,3,4,6,7,8,9,10,12,15,16,19],read_paramet:[2,10],readabl:[7,9],readi:[14,16],readlin:[9,12],reason:3,reassign:19,receiv:[0,2,9,10],recent:16,recogn:16,red:13,red_button:13,redirect:12,redistribut:0,refer:[3,18,19],referenc:18,reflect:16,regardless:7,register_palett:8,regular:18,rel:15,relat:16,remedi:6,remov:19,render:15,repli:[2,3,7,10,16,18,20],report:16,repr:4,repres:[3,4,6,7,10,16,18],represent:7,reprsent:16,request:[2,7,9],reserv:7,reset:15,resourc:9,respond:20,respons:[3,7],respresent:7,restructuredtext:9,result:7,revers:7,rotor:[7,16],round:4,rout:16,row:[14,15],rs485:7,run:[6,8,9,19],running_inst:19,runtim:3,runtimeerror:6,safe:12,safeguard:8,same:[3,4,6,7,9,12,14,15,16,20],save:[3,12,15,16],save_data:16,savingerror:3,screen:[8,13,15],script:[6,8],scroll:15,scrollabl:15,scrollablecommandlin:[8,15],scrollbar:15,scrollbutton:15,scroller:15,scroller_char:15,second:[10,16,19],see:[0,4,9,15,16,18],seem:19,select:15,self:[3,4,9,10,19,20],send:[2,8,9,10,19],sent:[2,3,7,10,16,18,19,20],sep:9,separ:6,sequenc:[4,14],serial:[2,7,10,19,20],serial_kwarg:10,serialexcept:2,set:[2,4,6,7,9,10,12,14,15,16,19],set_curr:7,set_flag_bit:7,set_frequ:7,set_paramerer_numb:7,set_parameter_index:7,set_parameter_mod:7,set_parameter_numb:7,set_parameter_valu:7,set_temperatur:7,set_text:8,set_voltag:7,setpoint:[7,16],setter:7,sever:9,share:[2,15],should:[0,4,7,8,9,10,12,14,15,16,18,19],show:[3,7],sign:4,signal:20,signatur:[4,10,19],signifi:6,similar:[3,4,13],simpl:[7,9],simpler:16,simpli:19,simul:[16,17,19,20],simultan:3,sinc:[3,4,7,10,16],singl:[4,7,9,15],sint:[4,7,16],size:[6,12,15,19],slave:7,sleep_tim:19,slice:4,smaller:4,smallest:4,softwar:0,sole:4,solv:3,some:[2,3,6,16,18,19],someth:3,sourc:[0,1],space:9,special:16,specif:3,specifi:[4,6,7,8,9,14,16,20],sphinx:3,split:9,stai:2,standard:12,start:[7,9,19],state:[8,10],stator:10,statu:[2,3,7,9,10,13,16],status_bit:10,status_format:[0,1,11],status_screen:13,statusbit:[3,7,10,16],stdin:9,stdout:9,step:[9,15,16],still:0,stop:[12,16,19,20],stopbit:10,store:[4,10,15,16],str:[3,4,6,7,10,14,15,18],string:[3,4,6,7,9,12,13,15],stringio:12,structur:[0,7],stx:7,style:8,subclass:[3,4,6,7,16,18],subpackag:[0,1,5,11,17],success:3,suitabl:19,superclass:[3,4],suppli:[4,16,19],support:7,sure:8,symbol:15,syntax:[3,6,7,9,16],sys:9,system:0,tabl:[0,1,9,11],team:0,telegram:[0,1,2,3,4,6,10,16,18,20],telegram_typ:3,telegrambuild:[7,16,18],telegramread:[2,7,10,16,18],tell:[2,3,15],temp_histori:15,temperatur:[7,10,16],temporarili:16,term:0,termin:[8,15],test:[0,6,7,14,16,17,20],test_:0,test_turboctl:0,text:[6,7,8,9,13,14,15],textiobas:12,than:[4,12,15],thei:[7,9,16],them:[16,18,19],thi:[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],those:[7,12,14,15,16],thread:[8,9,10,12,16,19,20],three:1,through:[7,8,10,15,16,19],thu:[7,20],time:[9,10,12,16],timeout:10,timestep:[10,16],togeth:3,top:15,total:16,total_row:15,toward:[15,16],traceback:[9,10,19,20],track:[10,15,16],tri:[3,7,16,20],ttyusb0:10,tupl:9,turboctl:[2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],turbovac:[0,3,5,7,17,20],turbovacuum:0,turn:[2,7,9,10,16],two:[4,15],txt:6,type:[3,4,6,7,8,9,10,12,15,16,18,19,20],type_:[7,19,20],typeerror:[4,7,9],typic:15,uint:[4,7,16,18],unalt:9,uncang:19,under:0,unindex:[2,3,6,10,18],uniniti:18,union:6,unit:[6,16],univers:0,unknown:3,unless:7,unlik:[9,16],unsign:4,until:19,unus:3,updat:[10,15,16],update_command:15,upon:[9,10,19,20],urwid:[8,13,15],usb:7,use:[3,7,9],used:[2,3,4,5,6,7,8,9,10,13,14,15,16,18,19,20],useful:0,user:[7,8,9,10,11,13,15,18,19],user_end:19,uses:[3,4,7,8,9,15],using:[7,9,12],uss:7,vacuum:7,valid:[4,7,20],valu:[2,3,4,6,7,9,10,12,14,15,16,18,19,20],valueerror:[2,3,4,7,9,10,14],variabl:[16,19],verbal:3,versa:16,version:[0,15,18],vertic:15,via:7,vice:16,view:15,virtual:[19,20],virtual_end:19,virtualconnect:[0,1,17,20],virtualpump:[0,1,16,18,19],visibl:15,visible_row:15,voltag:[7,10,16],wai:[3,7,9,20],wait:[8,9,16,19],warn:[6,9,14,16],warning_list:16,warranti:0,welcom:9,what:9,wheel:15,when:[3,4,6,7,8,9,15,16,19],whenev:[10,15],where:[7,9],whether:[3,6,7,10,12,15,16],which:[0,2,3,6,7,8,9,10,13,14,15,16,18,19],whitespac:9,widget:[0,1,11,13],width:[14,15],without:[0,3,7,12,16,17,19,20],work:[3,4,6,7,9,16,19],would:[3,6,12,20],wrap:[8,12,14],writabl:[6,18],write:[2,3,7,9,10,12,16,19],write_paramet:[2,10],written:[0,2,7,8,9,10,12,15,18,19],wrongnumerror:3,www:0,xor:7,you:0,your:0,zero:[4,7]},titles:["TurboCtl","turboctl","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">api</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">codes</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">datatypes</span></code>","telegram","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">parser</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">telegram</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">advanced_tui</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">command_line_ui</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">control_interface</span></code>","ui","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">queuefile</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">status_format</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">table</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">widgets</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">hardware_component</span></code>","virtualpump","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">parameter_component</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">virtualconnection</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">virtualpump</span></code>"],titleterms:{advanced_tui:8,api:2,author:0,code:3,command_line_ui:9,control_interfac:10,datatyp:4,document:0,hardware_compon:16,licens:0,parameter_compon:18,parser:6,queuefil:12,status_format:13,tabl:14,telegram:[5,7],turboctl:[0,1],virtualconnect:19,virtualpump:[17,20],widget:15}})