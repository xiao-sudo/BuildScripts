from .elem import ElemClass, ElemOrganization, Tab2DArray
from .proto_type_literals import INT, SINT, FIXED, STR
from .data import DataType


class ProtoTypeAssembler:
    builtin_repeated_message_names = {
        INT: 'IntArr',
        SINT: 'SIntArr',
        FIXED: 'FixedArr',
        STR: 'StrArr'
    }

    builtin_repeated_messages = {
        INT: "message %s {\n\trepeated int32 row=1\n}" % builtin_repeated_message_names[INT],
        SINT: "message %s {\n\trepeated sint32 row=1\n}" % builtin_repeated_message_names[SINT],
        FIXED: "message %s {\n\trepeated fixed32 row=1\n}" % builtin_repeated_message_names[FIXED],
        STR: "message %s {\n\trepeated string row=1\n}" % builtin_repeated_message_names[STR],
    }

    def assemble(self, data_type: DataType):
        return self.assemble_impl(data_type.elem_type, data_type.organization)

    def assemble_impl(self, elem_class: ElemClass, elem_organ: ElemOrganization):
        import_builtin = False
        if isinstance(elem_organ, Tab2DArray):
            proto_field_str = f'{elem_organ.to_proto_str()}' \
                              f'{self.builtin_repeated_message_names[elem_class.to_proto_str()]}'

            import_builtin = True
        else:
            proto_field_str = f'{elem_organ.to_proto_str()}{elem_class.to_proto_str()}'

        return [import_builtin, proto_field_str]
