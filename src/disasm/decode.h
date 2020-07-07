namespace captive {
  namespace arch {
    #define UNSIGNED_BITS(v, u, l) (((uint32_t)(v) << (31 - u)) >> (31 - u + l))
    #define SIGNED_BITS(v, u, l) (((int32_t)(v) << (31 - u)) >> (31 - u + l))
    #define BITSEL(v, b)   (((v) >> b) & 1UL)
    #define BIT_LSB(i)    (1 << (i))


		class JumpInfo {
		public:

			enum JumpType {
                     NONE,
                     DIRECT,
                     DIRECT_PREDICATED,
                     INDIRECT
			};

			JumpType type;
			uint64_t target;
		};


		class Decode {
		public:
			uint64_t pc;
			uint32_t length;

			bool end_of_block;
			bool is_predicated;

			virtual bool decode(uint32_t isa_mode, uint64_t insn_pc, const uint32_t *ptr) = 0;

			virtual JumpInfo get_jump_info() = 0;
		};
  }
}
