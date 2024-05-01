from fastapi import HTTPException


class Validator:
    @staticmethod
    def validate_location(location: str):
        if location not in ['inside', 'outside']:
            raise HTTPException(status_code=404, detail="%s is not a valid location" % location)