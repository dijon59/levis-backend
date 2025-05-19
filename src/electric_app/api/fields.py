from rest_framework import serializers


class EnumSerializer(serializers.ChoiceField):
    ENUM_FIELDS = ('name', 'value')

    def __init__(self, enum, enum_field='name', fields=None, choices=None, **kwargs):
        self.enum = enum
        if enum_field not in self.ENUM_FIELDS:
            raise ValueError('Invalid value for enum_field')
        self.enum_field = enum_field
        self.fields = fields  # ('name', 'value', 'label')
        if choices is None:
            self.enum_choices = list(enum)
        else:
            try:
                unique_choices = {e if isinstance(e, enum) else enum(e) for e in choices}
            except ValueError:
                raise ValueError('Choices should be an iterable of enum members or values.')
            else:
                self.enum_choices = sorted(unique_choices, key=list(enum).index)
        kwargs['choices'] = [(getattr(e, enum_field), e.name) for e in self.enum_choices]
        super(EnumSerializer, self).__init__(**kwargs)

    def to_representation(self, enum):
        if not enum:
            return None
        if self.fields:
            return {k: getattr(enum, k) for k in self.fields}
        else:
            return getattr(enum, self.enum_field)

    def to_internal_value(self, input_data):
        if input_data == '' and self.allow_blank:
            return None
        if isinstance(input_data, self.enum):
            return input_data
        try:
            if self.enum_field == 'value':
                converted_value = self.choice_strings_to_values[str(input_data)]
                return self.enum(converted_value)
            else:
                return getattr(self.enum, self.choices[input_data])
        except (AttributeError, KeyError, ValueError):
            self.fail('invalid_choice', input=input_data)
