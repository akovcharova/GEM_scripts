function Main() {
   var max_x = [];
   var max_y = [];
   var keepout_x = 35;
   var keepout_y = 60;
   // x are locations for via radii from strips.py
   // y are the segment edges
   max_x.push(724);  max_y.push(72);
   max_x.push(798);  max_y.push(84);
   max_x.push(881);  max_y.push(97);
   max_x.push(965);  max_y.push(111);
   max_x.push(1050); max_y.push(124);
   max_x.push(1137); max_y.push(141);
   max_x.push(1230); max_y.push(157);
   max_x.push(1331); max_y.push(174);

   PCBServer.PreProcess
   var board = PCBServer.GetCurrentPCBBoard
   if(board == null){
      ShowMessage("No PCB or footprint editor activated.")
   } else {
      board.XOrigin = 0
      board.YOrigin = MMsToCoord(400)
      // ShowMessage("Origin is at ("+board.XOrigin+","+board.YOrigin+")")
      // find net
      var Iterator = board.BoardIterator_Create;
      Iterator.AddFilter_ObjectSet(MkSet(eComponentObject));
      Iterator.AddFilter_LayerSet(AllLayers);
      Iterator.AddFilter_Method(eProcessAll);
      var conn = Iterator.FirstPCBObject;
      if (conn==null) {
         ShowMessage("No components found!")
         return;
      }
      var i=0;
      while (conn != null) {
         PCBServer.SendMessageToRobots(conn.I_ObjectAddress, c_Broadcast, 
                                       PCBM_BeginModify , c_NoEventData);

         var row = Math.floor(i/3);
         var x = max_x[row]-keepout_x;
         var y = 0;
         if (i%3==0) {
            x -= row*1.2;
            y -= max_y[row];
         }
         if (i%3==2) {
            x -= row*1.2;
            y += max_y[row];
         }
         x = board.XOrigin+MMsToCoord(x);
         y = board.YOrigin+MMsToCoord(y);
         conn.MoveToXY(x, y);
         conn.RotateBy(-90);

         PCBServer.SendMessageToRobots(conn.I_ObjectAddress, c_Broadcast, 
                                       PCBM_EndModify , c_NoEventData);
         conn = Iterator.NextPCBObject;
         i++;
      }


      board.BoardIterator_Destroy(Iterator);
      Client.SendMessage("PCB:Zoom", "Action=Redraw" , 255, Client.CurrentView)
   }
   PCBServer.PostProcess
}

