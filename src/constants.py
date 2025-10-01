from pydantic import BaseModel


class Constants(BaseModel):
  """Application constants."""

  successful_status: int = 200
  created_status: int = 201
  accepted_status: int = 202
  bad_request_status: int = 400
  unauthorized_status: int = 401
  forbidden_status: int = 403
  not_found_status: int = 404
  internal_server_error_status: int = 500
  service_unavailable_status: int = 503


constants = Constants()
