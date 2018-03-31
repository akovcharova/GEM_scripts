function Main() {
   var board_name = "GE21_M4";
   var debug = false;
   // offset of origin in Altium wrt AutoCAD
   if (debug) ShowMessage("Starting")
   var offset_x = 0;
   var offset_y = 400;
   if (board_name=="GE21_M4") {
      offset_x = -2000;
      offset_y = 620;
   }

   PCBServer.PreProcess
   var board = PCBServer.GetCurrentPCBBoard
   if(board == null){
      ShowMessage("No PCB or footprint editor activated.")
   } else {
      // make a list of all the old tracks to be duplicated before you've added new tracks...
      if (debug) ShowMessage("Making list of all the tracks")
      var track_iterator = board.BoardIterator_Create;
      track_iterator.AddFilter_ObjectSet(MkSet(eTrackObject));
      track_iterator.AddFilter_LayerSet(MkSet(eTopLayer));
      track_iterator.AddFilter_Method(eProcessAll);
      var itrack = track_iterator.FirstPCBObject;
      var track_list = [];
      while (itrack != null) {
         track_list.push(itrack);
         itrack = track_iterator.NextPCBObject;
      }
      board.BoardIterator_Destroy(track_iterator);

      // make list of all nets
      var net_iterator = board.BoardIterator_Create;
      net_iterator.AddFilter_ObjectSet(MkSet(eNetObject));
      net_iterator.AddFilter_LayerSet(AllLayers);
      net_iterator.AddFilter_Method(eProcessAll);
      var inet = net_iterator.FirstPCBObject;
      var net_list = [];
      while (inet != null) {
         net_list.push(inet);
         inet = net_iterator.NextPCBObject;
      }
      if (debug) ShowMessage("Number of nets found: " + net_list.length)
      board.BoardIterator_Destroy(net_iterator);


      // duplicate all tracks with mirror Y coordinate
      if (debug) ShowMessage("Duplicating tracks")
      for (var i=0; i < track_list.length; i++) {
         // do not mirror ground tracks for now
         if (debug) ShowMessage("Check for ground")
         if (track_list[i].Net.Name == "GND") continue;

         var track         = PCBServer.PCBObjectFactory(eTrackObject, eNoDimension, eCreate_Default);
         track.X1          = track_list[i].X1;
         track.Y1          = MMsToCoord(2*offset_y)-track_list[i].Y1;
         track.X2          = track_list[i].X2;
         track.Y2          = MMsToCoord(2*offset_y)-track_list[i].Y2;
         track.Layer       = track_list[i].Layer;
         track.Width       = track_list[i].Width;

         // assign net
         if (debug) ShowMessage("Assigning net")
         var old_name = track_list[i].Net.Name;
         var tmp = old_name.replace("C","").replace("V","").split("_");
         if (tmp.length != 2 || isNaN(tmp[0]) || isNaN(tmp[1])) {
            ShowMessage("Found bad net: "+old_name);
            break;
         }
         var iconn = parseInt(tmp[0]);
         if (iconn > 6) iconn = 12-(iconn-1)%6;
         else iconn = 6-(iconn-1);
         var ivia = 129-parseInt(tmp[1]);
         var new_name = "C"+iconn+"_V"+ivia;

         var found_net = false; 
         if (debug) ShowMessage("Looking for new net("+new_name+") for old net("+old_name+")");
         for (var j=0; j<net_list.length; j++) {
            if (net_list[j].Name == new_name) {
               found_net = true;
               track.Net = net_list[j];
               break;
            }
         }
         if (!found_net) ShowMessage("Could not find new net("+new_name+") for old net("+old_name+")");

         board.AddPCBObject(track);

         PCBServer.SendMessageToRobots(board.I_ObjectAddress, c_Broadcast, 
                                    PCBM_BoardRegisteration, track.I_ObjectAddress)
         if (debug && i>0) break;    
      }


      Client.SendMessage("PCB:Zoom", "Action=Redraw" , 255, Client.CurrentView)
   }
   PCBServer.PostProcess
}

