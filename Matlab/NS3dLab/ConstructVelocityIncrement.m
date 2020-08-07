FU = fftn(U); FV = fftn(V); FW = fftn(W); 


dU = (-U.*real(ifftn(iKX.*FU)) - V.*real(ifftn(iKY.*FU)) - W.*real(ifftn(iKZ.*FU))  - ...
      real(ifftn(iKX.*fftn(U.*U))) - real(ifftn(iKY.*fftn(V.*U))) - real(ifftn(iKZ.*fftn(W.*U))))*dt/2 ...
     + nu*dt*real(ifftn(DiffIF.*FU));

dV = (-U.*real(ifftn(iKX.*FV)) - V.*real(ifftn(iKY.*FV)) - W.*real(ifftn(iKZ.*FV))  - ...
      real(ifftn(iKX.*fftn(U.*V))) - real(ifftn(iKY.*fftn(V.*V))) - real(ifftn(iKZ.*fftn(W.*V))))*dt/2 ...
     + nu*dt*real(ifftn(DiffIF.*FV));

dW = (-U.*real(ifftn(iKX.*FW)) - V.*real(ifftn(iKY.*FW)) - W.*real(ifftn(iKZ.*FW))  - ...
      real(ifftn(iKX.*fftn(U.*W))) - real(ifftn(iKY.*fftn(V.*W))) - real(ifftn(iKZ.*fftn(W.*W))))*dt/2 ...
     + nu*dt*real(ifftn(DiffIF.*FW));

