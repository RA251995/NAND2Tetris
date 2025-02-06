# NAND to Tetris Course Notes
## Virtual Machine - Stack Machine
### Arithmetic / Logical Commands
![image](diagrams\drawio-assets\stack-arthimetic-logical-cmds.png)
 command | operation | returns
---------|-----------|---------
 `add`    | x+y       | integer
 `sub`    | x-y       | integer
 `neg`    | -y        | integer
 `eq`     | x==y      | boolean
 `gt`     | x>y       | boolean
 `lt`     | x<y       | boolean
 `and`    | x AND y   | boolean
 `or`     | x OR y    | boolean
 `not`    | NOT y     | boolean

### Push / Pop Commands
- `push segment i`
- `pop segment i`

#### Virtual Memory Segments
- constant

  `push constant i`: `RAM[SP] = i; SP++`

- local / argument / this / that

  `push <segment> i`: `addr = <BASE_ADDR> + i; RAM[SP] = RAM[addr]; SP++`

  `pop <segment> i`: `addr = <BASE_ADDR> + i; SP-; RAM[addr] = RAM[SP]`

  `<segment>` | `<BASE_ADDR>`
  ------------|---------------
   local      | `LCL`
   argument   | `ARG`
   this       | `THIS`
   that       | `THAT`

- static
  
  `push/pop static i`: `push/pop Xxx.i` while translating `Xxx.vm` file

- temp
  
  `push/pop temp i`: `push/pop RAM[5+i]`

- pointer
  
  `push/pop pointer 0`: `push/pop THIS`
  `push/pop pointer 1`: `push/pop THAT`

#### Standard VM Mapping