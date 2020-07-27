Search.setIndex({docnames:["index","installation","modules","modules/index","modules/telegram/api","modules/telegram/codes","modules/telegram/datatypes","modules/telegram/index","modules/telegram/parser","modules/telegram/telegram","modules/ui/advanced_tui","modules/ui/command_line_ui","modules/ui/control_interface","modules/ui/index","modules/ui/queuefile","modules/ui/status_format","modules/ui/table","modules/ui/widgets","modules/virtualpump/hardware_component","modules/virtualpump/index","modules/virtualpump/parameter_component","modules/virtualpump/virtualconnection","modules/virtualpump/virtualpump","notes","usage"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":2,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.intersphinx":1,sphinx:56},filenames:["index.rst","installation.rst","modules.rst","modules/index.rst","modules/telegram/api.rst","modules/telegram/codes.rst","modules/telegram/datatypes.rst","modules/telegram/index.rst","modules/telegram/parser.rst","modules/telegram/telegram.rst","modules/ui/advanced_tui.rst","modules/ui/command_line_ui.rst","modules/ui/control_interface.rst","modules/ui/index.rst","modules/ui/queuefile.rst","modules/ui/status_format.rst","modules/ui/table.rst","modules/ui/widgets.rst","modules/virtualpump/hardware_component.rst","modules/virtualpump/index.rst","modules/virtualpump/parameter_component.rst","modules/virtualpump/virtualconnection.rst","modules/virtualpump/virtualpump.rst","notes.rst","usage.rst"],objects:{"turboctl.telegram":{api:[4,0,0,"-"],codes:[5,0,0,"-"],datatypes:[6,0,0,"-"],parser:[8,0,0,"-"],telegram:[9,0,0,"-"]},"turboctl.telegram.api":{read_parameter:[4,1,1,""],send:[4,1,1,""],status:[4,1,1,""],write_parameter:[4,1,1,""]},"turboctl.telegram.codes":{AccessError:[5,2,1,""],CannotChangeError:[5,2,1,""],ControlBits:[5,3,1,""],CustomInt:[5,3,1,""],FlagBits:[5,3,1,""],MinMaxError:[5,2,1,""],OtherError:[5,2,1,""],ParameterAccess:[5,3,1,""],ParameterCode:[5,3,1,""],ParameterError:[5,3,1,""],ParameterException:[5,2,1,""],ParameterExceptionMeta:[5,3,1,""],ParameterIndexError:[5,2,1,""],ParameterResponse:[5,3,1,""],SavingError:[5,2,1,""],StatusBits:[5,3,1,""],WrongNumError:[5,2,1,""],get_parameter_code:[5,1,1,""],get_parameter_mode:[5,1,1,""]},"turboctl.telegram.codes.CustomInt":{__new__:[5,4,1,""]},"turboctl.telegram.codes.ParameterException":{member:[5,4,1,""]},"turboctl.telegram.codes.ParameterExceptionMeta":{member:[5,4,1,""]},"turboctl.telegram.datatypes":{BYTESIZE:[6,5,1,""],Bin:[6,3,1,""],Data:[6,3,1,""],Float:[6,3,1,""],Sint:[6,3,1,""],Uint:[6,3,1,""],maxsint:[6,1,1,""],maxuint:[6,1,1,""],minsint:[6,1,1,""]},"turboctl.telegram.datatypes.Bin":{__bytes__:[6,4,1,""],__init__:[6,4,1,""]},"turboctl.telegram.datatypes.Data":{__add__:[6,4,1,""],__eq__:[6,4,1,""],__getitem__:[6,4,1,""],__repr__:[6,4,1,""],bits:[6,4,1,""],n_bytes:[6,4,1,""],value:[6,4,1,""]},"turboctl.telegram.datatypes.Float":{__add__:[6,4,1,""],__bytes__:[6,4,1,""],__getitem__:[6,4,1,""],__init__:[6,4,1,""]},"turboctl.telegram.datatypes.Sint":{__bytes__:[6,4,1,""],__init__:[6,4,1,""]},"turboctl.telegram.datatypes.Uint":{__bytes__:[6,4,1,""],__init__:[6,4,1,""]},"turboctl.telegram.parser":{ERRORS:[8,6,1,""],ErrorOrWarning:[8,3,1,""],PARAMETERS:[8,6,1,""],Parameter:[8,3,1,""],WARNINGS:[8,6,1,""],load_errors:[8,1,1,""],load_parameters:[8,1,1,""],load_warnings:[8,1,1,""],main:[8,1,1,""]},"turboctl.telegram.parser.ErrorOrWarning":{fields:[8,4,1,""],name:[8,6,1,""],number:[8,6,1,""],possible_cause:[8,6,1,""],remedy:[8,6,1,""]},"turboctl.telegram.parser.Parameter":{"default":[8,6,1,""],bits:[8,6,1,""],datatype:[8,6,1,""],description:[8,6,1,""],fields:[8,4,1,""],indices:[8,6,1,""],max_value:[8,6,1,""],min_value:[8,6,1,""],name:[8,6,1,""],number:[8,6,1,""],unit:[8,6,1,""],writable:[8,6,1,""]},"turboctl.telegram.telegram":{Telegram:[9,3,1,""],TelegramBuilder:[9,3,1,""],TelegramReader:[9,3,1,""],checksum:[9,1,1,""]},"turboctl.telegram.telegram.Telegram":{LENGTH:[9,6,1,""],__bytes__:[9,4,1,""],current:[9,6,1,""],flag_bits:[9,6,1,""],frequency:[9,6,1,""],parameter_code:[9,6,1,""],parameter_index:[9,6,1,""],parameter_number:[9,6,1,""],parameter_value:[9,6,1,""],temperature:[9,6,1,""],voltage:[9,6,1,""]},"turboctl.telegram.telegram.TelegramBuilder":{__init__:[9,4,1,""],build:[9,4,1,""],from_bytes:[9,4,1,""],parameters:[9,6,1,""],set_current:[9,4,1,""],set_flag_bits:[9,4,1,""],set_frequency:[9,4,1,""],set_parameter_index:[9,4,1,""],set_parameter_mode:[9,4,1,""],set_parameter_number:[9,4,1,""],set_parameter_value:[9,4,1,""],set_temperature:[9,4,1,""],set_voltage:[9,4,1,""]},"turboctl.telegram.telegram.TelegramReader":{__init__:[9,4,1,""],__repr__:[9,4,1,""],__str__:[9,4,1,""],current:[9,4,1,""],flag_bits:[9,4,1,""],frequency:[9,4,1,""],parameter_error:[9,4,1,""],parameter_index:[9,4,1,""],parameter_mode:[9,4,1,""],parameter_number:[9,4,1,""],parameter_value:[9,4,1,""],telegram:[9,6,1,""],temperature:[9,4,1,""],type:[9,6,1,""],voltage:[9,4,1,""]},"turboctl.ui":{advanced_tui:[10,0,0,"-"],command_line_ui:[11,0,0,"-"],control_interface:[12,0,0,"-"],queuefile:[14,0,0,"-"],status_format:[15,0,0,"-"],table:[16,0,0,"-"],widgets:[17,0,0,"-"]},"turboctl.ui.advanced_tui":{AdvancedTUI:[10,3,1,""]},"turboctl.ui.advanced_tui.AdvancedTUI":{__init__:[10,4,1,""],command_line_interface:[10,6,1,""],display:[10,6,1,""],run:[10,4,1,""]},"turboctl.ui.command_line_ui":{CommandLineUI:[11,3,1,""]},"turboctl.ui.command_line_ui.CommandLineUI":{__enter__:[11,4,1,""],__exit__:[11,4,1,""],__init__:[11,4,1,""],cmd_debug:[11,4,1,""],cmd_exit:[11,4,1,""],cmd_help:[11,4,1,""],cmd_info:[11,4,1,""],cmd_list:[11,4,1,""],cmd_pump:[11,4,1,""],cmd_read:[11,4,1,""],cmd_status:[11,4,1,""],cmd_write:[11,4,1,""],cmds_and_aliases:[11,6,1,""],control_interface:[11,6,1,""],debug:[11,6,1,""],indent:[11,6,1,""],input:[11,4,1,""],inputfile:[11,6,1,""],intro:[11,6,1,""],outputfile:[11,6,1,""],print:[11,4,1,""],prompt:[11,6,1,""],run:[11,4,1,""]},"turboctl.ui.control_interface":{ControlInterface:[12,3,1,""],SERIAL_KWARGS:[12,5,1,""],Status:[12,3,1,""]},"turboctl.ui.control_interface.ControlInterface":{__enter__:[12,4,1,""],__exit__:[12,4,1,""],__init__:[12,4,1,""],close:[12,4,1,""],get_status:[12,4,1,""],pump_off:[12,4,1,""],pump_on:[12,4,1,""],read_parameter:[12,4,1,""],status:[12,6,1,""],timestep:[12,6,1,""],write_parameter:[12,4,1,""]},"turboctl.ui.control_interface.Status":{__setattr__:[12,4,1,""],callback:[12,6,1,""],current:[12,6,1,""],frequency:[12,6,1,""],pump_on:[12,6,1,""],status_bits:[12,6,1,""],temperature:[12,6,1,""],voltage:[12,6,1,""]},"turboctl.ui.queuefile":{QueueFile:[14,3,1,""]},"turboctl.ui.queuefile.QueueFile":{__init__:[14,4,1,""],block:[14,6,1,""],flush:[14,4,1,""],queue:[14,6,1,""],read:[14,4,1,""],readline:[14,4,1,""],write:[14,4,1,""]},"turboctl.ui.status_format":{green_button:[15,6,1,""],palette:[15,6,1,""],red_button:[15,6,1,""],status_screen:[15,1,1,""]},"turboctl.ui.table":{array:[16,1,1,""],table:[16,1,1,""]},"turboctl.ui.widgets":{CommandHistory:[17,3,1,""],CommandLines:[17,3,1,""],Position:[17,3,1,""],ScrollBar:[17,3,1,""],ScrollButton:[17,3,1,""],ScrollableCommandLines:[17,3,1,""],Scroller:[17,3,1,""]},"turboctl.ui.widgets.CommandHistory":{__init__:[17,4,1,""],down:[17,4,1,""],enter_command:[17,4,1,""],get_command:[17,4,1,""],history:[17,6,1,""],index:[17,6,1,""],temp_history:[17,6,1,""],up:[17,4,1,""],update_command:[17,4,1,""]},"turboctl.ui.widgets.CommandLines":{__init__:[17,4,1,""],edit:[17,6,1,""],enter:[17,4,1,""],history:[17,6,1,""],history_down:[17,4,1,""],history_up:[17,4,1,""],inputfile:[17,6,1,""],keypress:[17,4,1,""],move_cursor_to_end:[17,4,1,""],outputfile:[17,6,1,""],update:[17,4,1,""]},"turboctl.ui.widgets.Position":{__init__:[17,4,1,""],absolute:[17,6,1,""],listeners:[17,6,1,""],max_absolute:[17,4,1,""],relative:[17,6,1,""],total_rows:[17,6,1,""],visible_rows:[17,6,1,""]},"turboctl.ui.widgets.ScrollBar":{__init__:[17,4,1,""],background_char:[17,6,1,""],mouse_event:[17,4,1,""],position:[17,6,1,""],render:[17,4,1,""],scroller_char:[17,6,1,""]},"turboctl.ui.widgets.ScrollButton":{__init__:[17,4,1,""],mouse_event:[17,4,1,""],position:[17,6,1,""],step:[17,6,1,""]},"turboctl.ui.widgets.ScrollableCommandLines":{__init__:[17,4,1,""],arrow_down:[17,6,1,""],arrow_up:[17,6,1,""],command_lines:[17,6,1,""],position:[17,6,1,""],scrollbar:[17,6,1,""],scroller:[17,6,1,""]},"turboctl.ui.widgets.Scroller":{__init__:[17,4,1,""],keypress:[17,4,1,""],mouse_event:[17,4,1,""],position:[17,6,1,""],render:[17,4,1,""],widget:[17,6,1,""]},"turboctl.virtualpump":{hardware_component:[18,0,0,"-"],parameter_component:[20,0,0,"-"],virtualconnection:[21,0,0,"-"],virtualpump:[22,0,0,"-"]},"turboctl.virtualpump.hardware_component":{HWParameters:[18,3,1,""],HardwareComponent:[18,3,1,""],Variables:[18,3,1,""]},"turboctl.virtualpump.hardware_component.HWParameters":{__init__:[18,4,1,""],current:[18,6,1,""],error_counter:[18,6,1,""],error_frequency_list:[18,6,1,""],error_hour_list:[18,6,1,""],error_list:[18,6,1,""],frequency:[18,6,1,""],frequency_setpoint:[18,6,1,""],motor_power:[18,6,1,""],motor_temperature:[18,6,1,""],operating_hours:[18,6,1,""],overload_error_counter:[18,6,1,""],power_failure_error_counter:[18,6,1,""],save_data:[18,6,1,""],temperature:[18,6,1,""],voltage:[18,6,1,""],warning_list:[18,6,1,""]},"turboctl.virtualpump.hardware_component.HardwareComponent":{CURRENT:[18,6,1,""],TEMPERATURE:[18,6,1,""],VOLTAGE:[18,6,1,""],__init__:[18,4,1,""],abs_acceleration:[18,6,1,""],frequency:[18,6,1,""],handle_hardware:[18,4,1,""],is_on:[18,6,1,""],off:[18,4,1,""],on:[18,4,1,""],step:[18,6,1,""],stop:[18,4,1,""],variables:[18,6,1,""]},"turboctl.virtualpump.hardware_component.Variables":{__getattr__:[18,4,1,""],__init__:[18,4,1,""],__setattr__:[18,4,1,""],parameters:[18,6,1,""]},"turboctl.virtualpump.parameter_component":{ExtendedParameter:[20,3,1,""],ExtendedParameters:[20,3,1,""],ParameterComponent:[20,3,1,""]},"turboctl.virtualpump.parameter_component.ExtendedParameter":{"default":[20,6,1,""],__init__:[20,4,1,""],__str__:[20,4,1,""],bits:[20,6,1,""],datatype:[20,6,1,""],indices:[20,6,1,""],max_value:[20,4,1,""],min_value:[20,4,1,""],number:[20,6,1,""],parameters:[20,6,1,""],value:[20,6,1,""],writable:[20,6,1,""]},"turboctl.virtualpump.parameter_component.ExtendedParameters":{__init__:[20,4,1,""]},"turboctl.virtualpump.parameter_component.ParameterComponent":{__init__:[20,4,1,""],handle_parameter:[20,4,1,""],parameters:[20,6,1,""]},"turboctl.virtualpump.virtualconnection":{VirtualConnection:[21,3,1,""]},"turboctl.virtualpump.virtualconnection.VirtualConnection":{__enter__:[21,4,1,""],__exit__:[21,4,1,""],__init__:[21,4,1,""],buffer_size:[21,6,1,""],close:[21,4,1,""],close_all:[21,4,1,""],default_process:[21,4,1,""],is_running:[21,4,1,""],port:[21,4,1,""],process:[21,6,1,""],running_instances:[21,6,1,""],sleep_time:[21,6,1,""],thread:[21,6,1,""],user_end:[21,6,1,""],virtual_end:[21,6,1,""]},"turboctl.virtualpump.virtualpump":{VirtualPump:[22,3,1,""]},"turboctl.virtualpump.virtualpump.VirtualPump":{__enter__:[22,4,1,""],__exit__:[22,4,1,""],__init__:[22,4,1,""],connection:[22,6,1,""],hardware_component:[22,6,1,""],parameter_component:[22,6,1,""],process:[22,4,1,""],stop:[22,4,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","exception","Python exception"],"3":["py","class","Python class"],"4":["py","method","Python method"],"5":["py","data","Python data"],"6":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:function","2":"py:exception","3":"py:class","4":"py:method","5":"py:data","6":"py:attribute"},terms:{"boolean":12,"break":11,"byte":[6,9,21,22],"case":[6,8,9,18,20,21],"catch":[5,11],"class":[5,6,8,9,10,11,12,14,16,17,18,20,21,22],"default":[8,9,11,12,20,21,24],"enum":[5,9],"final":10,"float":[6,12,17,18,21],"function":[4,5,7,8,9,11,12,16,17,18,19,21,22],"import":8,"int":[5,6,8,9,12,16,17,20,21],"kivel\u00e4":0,"long":21,"new":[1,6,9,10,11,12,14,17,18,20,21,22],"public":0,"return":[4,5,6,8,9,11,12,14,15,16,17,18,20,21,22],"short":5,"static":[5,21],"true":[4,5,6,11,12,14,17,21],"try":[5,9,10],"while":[5,17,20],FOR:0,For:18,Its:[12,21],The:[0,2,3,4,5,6,8,9,10,11,12,14,15,16,17,18,20,21,22,24],These:11,Use:10,With:9,__add__:6,__bytes__:[6,9],__enter__:[11,12,21,22],__eq__:6,__exit__:[11,12,21,22],__getattr__:18,__getattribute__:18,__getitem__:6,__init__:[6,8,9,10,11,12,14,17,18,20,21,22],__main__:24,__new__:5,__repr__:[6,8,9],__setattr__:[12,18],__str__:[8,9,20],about:[4,8,11,12],abov:[9,17,18],abs_acceler:18,absolut:[17,24],acceler:18,accept:[5,6,11,24],access:[1,5,9,18,19,20,21,22],accesserror:5,accord:9,accordingli:[12,18],activ:11,actual:[9,18,19,20,21,22],add:[9,17],added:[1,4,9,24],addit:[1,2],address:9,adr:9,advanc:24,advanced_tui:[0,2,3,13],advancedtui:[10,15],affect:[8,9,12,18],after:[9,11,20,21],again:[11,21],algorithm:[9,11],alia:11,alias:11,all:[4,5,6,9,11,12,14,16,17,18,20,21,24],allow:18,along:0,alongsid:5,also:[1,2,4,5,8,9,11,12,17,21,24],altern:1,alwai:[5,6,9,14,17,18,20],among:17,amount:[17,18],analog:18,ani:[0,5,6,9,11,17,18,22,24],anoth:[1,8,11,17,20],api:[0,2,3,7],append:6,appli:18,approxim:17,aren:9,arg:[5,24],argument:[4,5,6,9,11,12,14,17,21,24],arrai:16,arrow:17,arrow_down:17,arrow_up:17,ask:[11,12],assign:[5,9,20,21],associ:9,attribut:[5,8,9,11,12,16,17,18,20,21],attributeerror:[5,14],auto_upd:[11,12],automat:[2,8,9,10,12,17,18,21,24],avoid:20,back:[4,12,20,22],background:11,background_char:17,bar:17,base:[5,6,9,10,17,20,21],basescreen:10,baudrat:12,bcc:9,beak:10,becaus:[5,6,9,11,18,20,24],been:[5,10,17,24],befor:[21,24],begin:[21,22],behav:20,behaviour:[8,14,17,22],being:[5,17],below:[9,10,17,18,24],between:[12,14,17,18],bin:[6,8,9],binari:6,bit:[4,5,6,8,9,18,20,21],block:[5,9,10,11,12,14,21,22],bool:[8,11,12,14,18],both:[4,5,9,12,18,20,24],bottom:17,bound:12,box:17,brows:17,buffer:21,buffer_s:21,build:[9,18],built:[5,9,10,11,18],button:17,byte_:9,bytes:[6,12],bytes_:9,bytes_in:22,call:[6,8,9,10,11,12,17,18,21,22,24],callabl:[10,12],callback:12,can:[0,1,4,5,6,8,9,11,12,14,16,17,18,19,20,21,22,24],cannot:[4,5,6,8,9,11,18,20,22],cannotchangeerror:5,canva:17,caught:11,caus:[4,8,18],celsiu:8,chang:[5,8,9,10,12,17,18,20,22],charact:[5,6,14,17],check:[9,21],checksum:9,choos:1,circl:15,circuit:[9,12,18],circular:5,circumv:5,classmethod:21,classnam:[6,9],click:17,close:[10,11,12,21,22],close_al:21,cls:5,cmd_:11,cmd_debug:11,cmd_exampl:11,cmd_exit:11,cmd_help:11,cmd_info:11,cmd_list:11,cmd_pump:11,cmd_read:11,cmd_statu:11,cmd_write:11,cmds_and_alias:11,code:[0,2,3,7,9,10,18,21],col:17,collect:18,colour:15,column:16,combin:[6,10],command:[4,9,10,11,12,17,18,20,21,22,24],command_lin:17,command_line_interfac:10,command_line_ui:[0,2,3,13],commandhistori:17,commandlin:17,commandlineui:[10,11],common:4,commun:[7,9,10,21],complement:6,compon:18,compos:6,comput:[5,9],condit:[5,8,9,12,18],connect:[4,12,21,22,24],consecut:17,consist:[9,17],constant:18,construct:[9,20],consum:11,contact:0,contain:[2,3,4,5,6,7,8,9,11,13,14,17,18,19],content:[9,10,12,15,22],continu:[11,21],control:[0,4,5,9,10,11,14,15,18],control_interfac:[0,2,3,11,13],controlbit:[5,9,18],controlinterfac:[11,12],convent:9,convert:[9,12,18],copi:[0,9,20],copyright:0,correct:5,correctli:18,correspond:[2,5,8,9,11,16,18,20],count:[17,18],crash:[10,11],creat:[5,7,8,9,11,12,14,16,17,21,24],cumbersom:9,current:[8,9,12,17,18,20,21],cursor:17,custom:[5,9],customint:5,cut:18,data:[4,6,8,9,18,20,21,22],databas:16,dataclass:[8,9],datatyp:[0,2,3,7,8,9,18,20],deactiv:11,debug:11,deceler:18,decreas:17,default_process:21,defin:[4,5,6,8,9,10,11,12,14,17,18,20,24],degre:8,del:21,denot:9,depend:[0,5,8,9,11,20],describ:[5,8,11,20],descript:[5,8,18],descriptor:21,detail:[0,1,6,9,11],determin:[9,12],dev:[12,21,24],develop:0,devic:[12,21],dict:[8,9,16,18,20],dictionari:8,differ:[5,6,8,9,14,17],direct:5,directli:[6,9],directori:[0,8,24],disabl:11,displai:[10,11,15,16,17,20],distribut:0,disturb:18,divid:[3,6],docstr:[11,17],document:10,doe:14,doesn:[1,5,9,11,21,24],doing:21,done:[17,24],down:17,download:1,draw:17,due:4,dummi:18,dure:11,each:[5,9,11,16,17,18,20],easier:[11,14],easiest:5,easili:[5,9,11,14,24],edg:17,edit:[11,17],effect:17,either:0,empti:[4,6,12,16,17,22],emul:[14,17],enabl:[9,22],encapsul:18,encount:14,end:[6,9,10,11,17,21],enter:[10,11,12,17],enter_command:17,entri:[9,10,17],enumnam:5,equal:[6,17],error:[4,5,8,9,11,16,18,20],error_count:18,error_frequency_list:18,error_hour_list:18,error_list:18,errororwarn:[8,16],etc:17,eval:9,evalu:[4,9],even:[0,9,18,20],event:17,everi:[11,12,18,24],exact:[9,18],exactli:[5,6],exampl:[6,9,10,11,20,24],exc_typ:12,exc_valu:12,except:[5,6],exception_typ:11,exception_valu:11,exclud:9,exclus:9,execut:[8,10,11],exist:[5,6,9,11,14],exit:[10,11,12,21,22],expand:18,explain:[8,15,17],explicitli:[9,12],express:6,extend:20,extended_paramet:20,extendedparamet:[18,20],extern:1,factori:12,fail:9,fals:[4,5,6,11,12,14,17,21],far:17,fast:18,felik:0,field:[5,8,10,16,18],file:[8,10,11,14,17,21],filenam:8,filenotfounderror:8,fill:24,find:18,first:[5,9],firstnam:0,fit:0,fix:17,flag:[12,14,18],flag_bit:9,flagbit:5,flow:17,flush:[11,14],focu:17,follow:[1,2,3,4,5,6,9,11,18,20,21,24],form:[6,11,12,17,21,22],format:[6,9,10,15,16,20],found:[8,18,20],foundat:0,four:11,free:[0,21],freez:18,frequenc:[9,12,18],frequency_setpoint:18,friendli:9,from:[5,8,9,10,11,14,17,18,20,21,22,24],from_byt:9,full:6,fusor:0,futur:18,gener:[0,8,9,17],get:[6,11],get_command:17,get_parameter_cod:5,get_parameter_mod:5,get_statu:12,give:[5,6,11,17,18],given:[6,9,11,12,14,17,18,21],gnu:0,gradual:18,green:15,green_button:15,group:5,handl:[17,18,20,21,22],handle_hardwar:18,handle_paramet:[18,20],happen:14,hardwar:[18,22],hardware_compon:[0,2,3,19,22],hardwarecompon:[18,22],has:[2,5,8,9,11,17,18,20,21,24],hasn:10,have:[0,2,4,5,6,8,9,12,18,21,24],height:17,help:[11,24],helsinki:0,here:[9,15,17,21],histori:17,history_down:17,history_up:17,hold:[8,20],hope:0,hour:18,how:[6,9,15,17,18,21],howev:[5,9,18],http:0,human:[9,11],hvctl:[0,24],hwparamet:18,ident:17,ieee:6,ignor:[11,12,18],immut:20,impli:0,includ:[1,9,11,14,17,18],incom:22,incompat:24,increas:17,ind:9,indent:11,index:[4,5,6,8,9,11,12,17,18],indic:[8,9,14,18,20],infinit:16,info:11,inform:[10,11,12],inherit:5,initi:[5,6,9,10,11,12,15,17,18,20,21,22],input:[10,11,14,17,18,21],input_:21,inputfil:[10,11,17],ins:9,insid:24,instal:[0,10],instanc:[4,5,6,9,11,12,18,20,21],instead:[5,6,8,9,10,11,15,16,17,18,21,24],integ:[6,18],intend:[0,1],interfac:[1,10,11,13,14,17,24],intermedi:[9,12,18],intern:2,interpret:[9,15,21,22],intial:14,intro:11,invalid:[4,5,6,9,11,12],invis:17,ipsum:23,is_on:18,is_run:21,isn:[5,8,9,11,12,16,24],issu:10,iter:[9,10,11,15,17,18],its:[5,8,9,10,11,14,17,21,22],itself:5,just:9,keep:[12,17,18],kei:[6,8,9,16,17,20],keyerror:20,keypress:17,keyword:12,kwarg:5,lack:[5,6],largest:6,lastnam:0,later:[0,17],latest:17,least:18,left:[10,17],len:6,length:[6,9,17,20],less:[6,11,14],letter:11,leybold:[0,9],lge:9,librari:[1,17],like:[5,6,8,10,11,14,17,20,21],likewis:6,line:[8,10,11,17,24],linux:[0,1,17],list:[8,9,11,12,16,17,18,20,24],listen:17,load_error:8,load_paramet:8,load_warn:8,locat:[1,2,8,10,17,18],lock:18,longer:11,loop:[10,11],lorem:23,lost:18,machin:21,made:[1,17],mai:[6,9,10,11,17],main:[8,10],mainloop:10,make:[5,10,11,14,17,18,22,24],mani:[6,21],manner:21,manual:[9,20],match:[5,6,18],max_absolut:17,max_valu:[8,20],maximum:[8,16,17,20],maxsint:6,maxuint:6,mean:[5,8,9],meant:[5,6,21],member:[5,9,12],member_nam:5,member_valu:5,memori:[5,17,18],merchant:0,messag:[5,9,11,24],metaclass:5,method:[5,6,8,9,10,11,12,14,18,21],min_valu:[8,20],minimum:[8,20],minmaxerror:5,minsint:6,minumum:8,mirror:2,mode:[5,9,11],modifi:[0,17,18],modul:[0,4,5,6,8,9,10,11,14,15,16,17,18,20,21,22],modulenam:2,more:[0,6,9,24],most:[2,6,18,20,21],motor:[9,12,18],motor_pow:18,motor_temperatur:18,mous:17,mouse_ev:17,move:[17,18],move_cursor_to_end:17,multipl:[5,8,17],multipli:6,must:[5,6,9,12],n_byte:6,name:[8,9,11,12,16,18,21],nan:6,need:[5,6,11,18,20],neg:[6,9,17],nest:15,never:14,newer:17,newest:17,newlin:14,node:9,non:[5,6,9,20],none:[6,8,9,11,12,14,17,21],nonvolatil:[5,18],normal:[9,11,18],note:[0,9,12,18],noth:[14,17],number:[4,5,6,8,9,11,12,14,16,17,18,20],object:[5,6,8,9,10,11,12,14,15,16,17,18,20,21,22],occur:18,off:[4,11,12,18],often:5,old:17,older:17,oldest:[17,18],onc:21,one:[5,9,12,14,17,24],ones:17,onli:[5,6,9,11,12,17,18,20,21],open:11,openpti:14,oper:[0,1,9,11,18],operating_hour:18,option:[0,6,24],order:[1,5,8,11,18,20],ordereddict:8,org:0,origin:[17,20],other:[1,5,6,9,17,18,20,21],othererror:5,otherwis:[4,5,6,9,11,12,17,18,21],out:18,output:[10,11,14,17,21],outputfil:[10,11,17],outsid:5,overload:18,overload_error_count:18,overrid:9,p18:[8,20],packag:[0,1,3,22,24],pad:6,palett:[10,15],parallel:[10,11,12,18,21,22],param_channel:18,paramet:[4,5,6,8,9,10,11,12,15,16,17,18,20,21,22],parameter_cod:9,parameter_compon:[0,2,3,19,22],parameter_error:9,parameter_index:9,parameter_mod:9,parameter_nam:18,parameter_numb:9,parameter_valu:9,parameteraccess:5,parametercod:5,parametercompon:[18,20,22],parametererror:[5,9],parametererrorx:5,parameterexcept:5,parameterexceptionmeta:5,parameterindexerror:5,parameterrespons:5,pariti:[9,12],pars:[8,11],parser:[0,2,3,7],part:[14,17,18,20],particular:0,pass:[5,9,10,11,12,17,18],path:[1,8,24],pattern:11,perform:22,permit:9,physic:22,pke:9,plain:11,point:[6,17],poll:11,port:[9,11,12,21,24],portion:17,posit:[6,17,18],possibl:[5,8,14,18,21,22,24],possible_caus:8,power:[9,18],power_failure_error_count:18,precis:6,present:[5,10,15,18],press:17,prevent:[5,10,11,18],previou:17,previous:17,print:[10,11,14,16,17],probabl:[1,10],problem:5,process:[21,22],process_channel:18,program:[0,5,10,11,13,14,19,22],prompt:11,properli:5,properti:[5,6,8,9,17,18,20,21],protocol:9,provid:[11,17,24],pts:21,pty:14,publish:0,pump:[0,4,5,7,8,9,11,12,15,18,19,20,22,24],pump_off:12,pump_on:[4,12],purpos:[0,8,9,18],pwe:9,pyseri:1,python:[0,1,5,9,18,21,24],pythonpath:1,pzd1:9,pzd2:9,pzd3:9,pzd4:9,pzd6:9,queri:[4,5,9,12,18,20],queue:14,queuefil:[0,2,3,13],race:18,rais:[4,5,6,8,9,11,12,14,16,20],rang:[5,6,8],rate:18,read:[4,5,6,8,9,10,11,12,14,17,18,21],read_paramet:[4,12],readabl:[9,11],readi:[16,18],readlin:[11,14],real:24,reason:5,reassign:21,receiv:[0,4,11,12],recent:18,recogn:18,red:15,red_button:15,redirect:14,redistribut:0,refer:[5,20,21],referenc:20,reflect:18,regardless:9,register_palett:10,regular:20,rel:[1,17,24],relat:18,remedi:8,remov:21,render:17,repli:[4,5,9,12,18,20,22],report:18,repr:6,repres:[5,6,8,9,12,18,20],represent:9,reprsent:18,request:[4,9,11],requir:24,reserv:9,reset:17,resourc:11,respond:22,respons:[5,9],respresent:9,restructuredtext:11,result:9,revers:9,rotor:[9,18],round:6,rout:18,row:[16,17],rs485:9,run:[0,1,8,10,11,21],running_inst:21,runtim:5,runtimeerror:8,safe:14,safeguard:10,same:[5,6,8,9,11,14,16,17,18,22],save:[5,14,17,18],save_data:18,savingerror:5,screen:[10,15,17],script:[1,8,10,24],scroll:17,scrollabl:17,scrollablecommandlin:[10,17],scrollbar:17,scrollbutton:17,scroller:17,scroller_char:17,second:[12,18,21],see:[0,1,6,11,17,18,20,24],seem:21,select:17,self:[5,6,11,12,21,22],send:[4,10,11,12,21,24],sent:[4,5,9,12,18,20,21,22],sep:11,separ:8,sequenc:[6,16],serial:[4,9,12,21,22,24],serial_kwarg:12,serialexcept:4,set:[4,6,8,9,11,12,14,16,17,18,21],set_curr:9,set_flag_bit:9,set_frequ:9,set_paramerer_numb:9,set_parameter_index:9,set_parameter_mod:9,set_parameter_numb:9,set_parameter_valu:9,set_temperatur:9,set_text:10,set_voltag:9,setpoint:[9,18],setter:9,sever:11,share:[4,17],shell:24,should:[0,1,6,9,10,11,12,14,16,17,18,20,21],show:[5,9,24],sign:6,signal:22,signatur:[6,12,21],signifi:8,similar:[5,6,15],simpl:[9,11,24],simpler:18,simpli:[1,21],simul:[18,19,21,22,24],simultan:5,sinc:[5,6,9,12,18],singl:[6,9,11,17],sint:[6,9,18],size:[8,14,17,21],slave:9,sleep_tim:21,slice:6,smaller:6,smallest:6,softwar:0,sole:6,solv:5,some:[1,4,5,8,18,20,21],someth:5,sourc:[2,3],space:11,special:18,specif:5,specifi:[6,8,9,10,11,16,18,22],sphinx:5,split:11,stai:4,standard:[1,14],start:[9,11,21],state:[10,12],stator:12,statu:[4,5,9,11,12,15,18],status_bit:12,status_format:[0,2,3,13],status_screen:15,statusbit:[5,9,12,18],stdin:11,stdout:11,step:[11,17,18],still:0,stop:[14,18,21,22],stopbit:12,store:[6,12,17,18],str:[5,6,8,9,12,16,17,20],string:[5,6,8,9,11,14,15,17],stringio:14,structur:[2,9],stx:9,style:10,subclass:[5,6,8,9,18,20],subpackag:[2,3,7,13,19],success:5,suitabl:21,superclass:[5,6],suppli:[6,18,21,24],support:9,sure:10,symbol:17,syntax:[5,8,9,11,18],sys:11,system:[0,1],tabl:[0,2,3,11,13],tabul:1,team:0,telegram:[0,2,3,4,5,6,8,12,18,20,22],telegram_typ:5,telegrambuild:[9,18,20],telegramread:[4,9,12,18,20],tell:[4,5,17],temp_histori:17,temperatur:[9,12,18],temporarili:18,term:0,termin:[10,17],test:[1,2,8,9,16,18,19,22,24],test_:2,test_turboctl:2,text:[8,9,10,11,15,16,17],textiobas:14,than:[6,14,17],thei:[9,11,18],them:[18,20,21],thi:[0,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24],those:[9,14,16,17,18],thread:[10,11,12,14,18,21,22],three:3,through:[9,10,12,17,18,21],thu:[9,22],time:[11,12,14,18,24],timeout:12,timestep:[12,18],togeth:5,top:17,total:18,total_row:17,toward:[17,18],traceback:[11,12,21,22],track:[12,17,18],tri:[5,9,18,22],ttyusb0:[12,24],tupl:11,turboctl:[2,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24],turbovac:[0,5,7,9,19,22],turbovacuum:0,turn:[4,9,11,12,18],tweak:1,two:[6,17],txt:8,type:[5,6,8,9,10,11,12,14,17,18,20,21,22],type_:[9,21,22],typeerror:[6,9,11],typic:17,uint:[6,9,18,20],unalt:11,uncang:21,under:0,unindex:[4,5,8,12,20],uniniti:20,union:8,unit:[8,18],univers:0,unknown:5,unless:9,unlik:[11,18],unsign:6,until:21,unus:5,updat:[12,17,18],update_command:17,upon:[11,12,21,22],urwid:[1,10,15,17,24],usag:[0,1],usb:9,use:[5,9,11],used:[1,4,5,6,7,8,9,10,11,12,15,16,17,18,20,21,22,24],useful:0,user:[1,9,10,11,12,13,15,17,20,21],user_end:21,uses:[1,5,6,9,10,11,17],using:[1,9,11,14],uss:9,vacuum:9,valid:[6,9,22],valu:[4,5,6,8,9,11,12,14,16,17,18,20,21,22],valueerror:[4,5,6,9,11,12,16],variabl:[18,21],verbal:5,versa:18,version:[0,1,17,20],vertic:17,via:[9,24],vice:18,view:17,virtual:[21,22,24],virtual_end:21,virtualconnect:[0,2,3,19,22],virtualpump:[0,2,3,18,20,21],visibl:17,visible_row:17,voltag:[9,12,18],wai:[5,9,11,22],wait:[10,11,18,21],warn:[8,11,16,18],warning_list:18,warranti:0,welcom:11,what:11,wheel:17,when:[5,6,8,9,10,11,17,18,21],whenev:[12,17],where:[9,11],whether:[5,8,9,12,14,17,18],which:[2,4,5,8,9,10,11,12,15,16,17,18,20,21,24],whitespac:11,widget:[0,2,3,13,15],width:[16,17],window:1,without:[0,1,5,9,14,18,19,21,22,24],won:1,work:[1,5,6,8,9,11,18,21],would:[5,8,14,22],wrap:[10,14,16],writabl:[8,20],write:[4,5,9,11,12,14,18,21],write_paramet:[4,12],written:[0,1,4,9,10,11,12,14,17,20,21],wrongnumerror:5,www:0,xor:9,you:0,your:[0,1],zero:[6,9]},titles:["TurboCtl","Installation","Packages and modules","turboctl","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">api</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">codes</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">datatypes</span></code>","telegram","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">parser</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">telegram</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">advanced_tui</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">command_line_ui</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">control_interface</span></code>","ui","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">queuefile</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">status_format</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">table</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">widgets</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">hardware_component</span></code>","virtualpump","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">parameter_component</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">virtualconnection</span></code>","<code class=\"xref py py-mod docutils literal notranslate\"><span class=\"pre\">virtualpump</span></code>","Notes","Usage"],titleterms:{The:1,advanced_tui:10,api:4,author:0,code:5,command_line_ui:11,control_interfac:12,datatyp:6,depend:1,directori:1,document:0,hardware_compon:18,instal:1,licens:0,modul:2,note:23,packag:2,parameter_compon:20,parser:8,program:24,queuefil:14,run:24,start:[],status_format:15,tabl:16,telegram:[7,9],turboctl:[0,1,3],usag:24,virtualconnect:21,virtualpump:[19,22],widget:17}})