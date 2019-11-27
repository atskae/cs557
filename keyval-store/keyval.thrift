exception SystemException {
  1: optional string message
}

struct NodeID {
  1: string id;
  2: string ip;
  3: i32 port;
}

enum ConstMethod {
  READ_REPAIR = 1,
  HINTED_HANDOFF = 2
}

enum ConstLevel {
  ONE = 1,
  QUORUM = 2
}

service KeyValStore {

  void initServer(1: list<NodeID> node_list, 2: ConstMethod constMethod),

  string get(1: i8 key, 2: ConstLevel constLevel)
    throws (1: SystemException systemException),
  
  void put(1: i8 key, 2: string val, 3: ConstLevel constLevel)
    throws (1: SystemException systemException)

}
