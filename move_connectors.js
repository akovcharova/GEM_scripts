function Main() {
   var board_name = "GE21_M4";
   // offset of origin in Altium wrt AutoCAD
   var offset_x = 0;
   var offset_y = 400;
   if (board_name=="GE21_M4") {
      offset_x = -2000;
      offset_y = 620;
   }
   // x are locations for via radii from strips.py
   // y are the segment edges
   var max_x = [];
   var max_y = [];
   if (board_name=="ME0") {
      max_x.push(724-35);  max_y.push(72);
      max_x.push(798-35);  max_y.push(84);
      max_x.push(881-35);  max_y.push(97);
      max_x.push(965-35);  max_y.push(111);
      max_x.push(1050-35); max_y.push(124);
      max_x.push(1137-35); max_y.push(141);
      max_x.push(1230-35); max_y.push(157);
      max_x.push(1331-35); max_y.push(174);
   } else if (board_name=="GE21_M4"){
      max_x.push(2726+190);  max_y.push(541-150-5);
      max_x.push(2726+300);  max_y.push(561-150-5);
   }

   PCBServer.PreProcess
   var board = PCBServer.GetCurrentPCBBoard
   if(board == null){
      ShowMessage("No PCB or footprint editor activated.")
   } else {
      // find ground net
      var net_it = board.BoardIterator_Create;
      net_it.AddFilter_ObjectSet(MkSet(eNetObject));
      net_it.AddFilter_LayerSet(AllLayers);
      net_it.AddFilter_Method(eProcessAll);
      var net = net_it.FirstPCBObject;
      while (net != null && net.Name != "GND") {
         net = net_it.NextPCBObject;
      }

      // find connectors
      var comp_iterator = board.BoardIterator_Create;
      comp_iterator.AddFilter_ObjectSet(MkSet(eComponentObject));
      comp_iterator.AddFilter_LayerSet(AllLayers);
      comp_iterator.AddFilter_Method(eProcessAll);
      var conn = comp_iterator.FirstPCBObject;
      if (conn==null) {
         ShowMessage("No components found!")
         return;
      } 
      var i=0;
      while (conn != null) {
         PCBServer.SendMessageToRobots(conn.I_ObjectAddress, c_Broadcast, 
                                       PCBM_BeginModify , c_NoEventData);

         var row = Math.floor(i/3);
         if (board_name!="ME0") row = Math.floor(i/6);

         var x = max_x[row];
         var y = 0;
         if (board_name=="ME0") {
            if (i%3==0) {
               x -= row*1.2;
               y -= max_y[row];
            }
            if (i%3==2) {
               x -= row*1.2;
               y += max_y[row];
            }
         } else if (board_name=="GE21_M4") {
            y = (i%6)*2*max_y[row]/5-max_y[row];
         }
         x += offset_x;
         y += offset_y;

         conn.MoveToXY(MMsToCoord(x), MMsToCoord(y));
         if (board_name=="GE21_M4" && row==0) conn.RotateBy(90);
         else conn.RotateBy(-90);
         PCBServer.SendMessageToRobots(conn.I_ObjectAddress, c_Broadcast, 
                                       PCBM_EndModify , c_NoEventData);

         // determine all the coordinates for the connector ground skeleton
         var gnd_x = [];
         var gnd_y = [];

         // spine
         var spine_len = 40;
         gnd_x.push(x-spine_len/2);      gnd_y.push(y); //start
         gnd_x.push(x+spine_len/2);      gnd_y.push(y); //end

         // fork at start
         gnd_x.push(gnd_x[0]);          gnd_y.push(gnd_y[0]);     // fork up
         gnd_x.push(gnd_x[0]-1.3);      gnd_y.push(gnd_y[0]+1.3);          
         gnd_x.push(gnd_x[0]-1.3);      gnd_y.push(gnd_y[0]+1.3); // lengthen
         gnd_x.push(gnd_x[0]-1.3-2.3);  gnd_y.push(gnd_y[0]+1.3); 
         gnd_x.push(gnd_x[0]);          gnd_y.push(gnd_y[0]);     // fork down
         gnd_x.push(gnd_x[0]-1.3);      gnd_y.push(gnd_y[0]-1.3);          
         gnd_x.push(gnd_x[0]-1.3);      gnd_y.push(gnd_y[0]-1.3); // lengthen
         gnd_x.push(gnd_x[0]-1.3-2.3);  gnd_y.push(gnd_y[0]-1.3); 

         // fork at end
         gnd_x.push(gnd_x[1]);          gnd_y.push(gnd_y[1]);     // fork up
         gnd_x.push(gnd_x[1]+1.3);      gnd_y.push(gnd_y[1]+1.3);          
         gnd_x.push(gnd_x[1]+1.3);      gnd_y.push(gnd_y[1]+1.3); // lengthen
         gnd_x.push(gnd_x[1]+1.3+2.3);  gnd_y.push(gnd_y[1]+1.3); 
         gnd_x.push(gnd_x[1]);          gnd_y.push(gnd_y[1]);     // fork down
         gnd_x.push(gnd_x[1]+1.3);      gnd_y.push(gnd_y[1]-1.3);          
         gnd_x.push(gnd_x[1]+1.3);      gnd_y.push(gnd_y[1]-1.3); // lengthen
         gnd_x.push(gnd_x[1]+1.3+2.3);  gnd_y.push(gnd_y[1]-1.3); 

         // ribs
         var rib_gap = 6;
         var rib_len = 6;
         for (var irib=0; irib<7; irib++){
            gnd_x.push(x+(irib-3)*rib_gap);         gnd_y.push(y+rib_len/2);
            gnd_x.push(x+(irib-3)*rib_gap);         gnd_y.push(y-rib_len/2);
         }

         // place ground skeleton
         for (var itrack=0; itrack<(Math.floor(gnd_x.length/2)); itrack++){
            var ind = 2*itrack;
            var track         = PCBServer.PCBObjectFactory(eTrackObject, eNoDimension, eCreate_Default);
            track.X1          = MMsToCoord(gnd_x[ind]);
            track.Y1          = MMsToCoord(gnd_y[ind]);
            track.X2          = MMsToCoord(gnd_x[ind+1]);
            track.Y2          = MMsToCoord(gnd_y[ind+1]);
            track.Layer       = eTopLayer;
            track.Width       = MMsToCoord(0.5);
            track.Net         = net;
            board.AddPCBObject(track);

            PCBServer.SendMessageToRobots(board.I_ObjectAddress, c_Broadcast, 
                                       PCBM_BoardRegisteration, track.I_ObjectAddress)
         }

         conn = comp_iterator.NextPCBObject;
         i++;
      }


      board.BoardIterator_Destroy(comp_iterator);
      board.BoardIterator_Destroy(net_it);
      Client.SendMessage("PCB:Zoom", "Action=Redraw" , 255, Client.CurrentView)
   }
   PCBServer.PostProcess
}

