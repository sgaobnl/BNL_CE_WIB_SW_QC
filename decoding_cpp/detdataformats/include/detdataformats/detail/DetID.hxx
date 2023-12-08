
namespace dunedaq::detdataformats {

static_assert(DetID::s_det_id_version == 1,
              "This is intentionally designed to tell the developer to update the static_assert checks (including this "
              "one) when the version is bumped");
static_assert(sizeof(DetID) == 4, "DetID struct size different than expected!");
static_assert(offsetof(DetID, version) == 0, "DetID version field not at expected offset");
static_assert(offsetof(DetID, subdetector) == 2, "DetID subdetector field not at expected offset");

/**
 * @brief Stream a Subdetector instance in a human-readable form
 * @param o Stream to output to
 * @param id Subdetector to stream
 * @return Stream instance for further streaming
 */
inline std::ostream&
operator<<(std::ostream& o, DetID::Subdetector const& type)
{
  return o << DetID::subdetector_to_string(type);
}

/**
 * @brief Stream a DetID instance in a human-readable form
 * @param o Stream to output to
 * @param id DetID to stream
 * @return Stream instance for further streaming
 */
inline std::ostream&
operator<<(std::ostream& o, DetID const& det_id)
{
  return o << "subdetector: " << det_id.subdetector ;
}

/**
 * @brief Read a DetID::Subdetector from a string stream
 * @param is Stream to read from
 * @param id Subdetector to fill
 * @return Stream instance for further streaming
 */
inline std::istream&
operator>>(std::istream& is, DetID::Subdetector& t)
{
  std::string tmp;
  is >> tmp;

  t = DetID::string_to_subdetector(tmp);

  return is;
}
/**
 * @brief Read a DetID from a string stream
 * @param is Stream to read from
 * @param id DetID to fill
 * @return Stream instance for further streaming
 */
inline std::istream&
operator>>(std::istream& is, DetID& det_id)
{
  std::string tmp;
  is >> tmp >> det_id.subdetector; 

  return is;
}

std::string
DetID::subdetector_to_string(const Subdetector& type)
{
  switch (type) {
    case Subdetector::kDAQ:
      return "DAQ";
    case Subdetector::kHD_PDS:
      return "HD_PDS";
    case Subdetector::kHD_TPC:
      return "HD_TPC";
    case Subdetector::kHD_CRT:
      return "HD_CRT";
    case Subdetector::kVD_CathodePDS:
      return "VD_Cathode_PDS";
    case Subdetector::kVD_MembranePDS:
      return "VD_Membrane_PDS";
    case Subdetector::kVD_BottomTPC:
      return "VD_Bottom_TPC";
    case Subdetector::kVD_TopTPC:
      return "VD_Top_TPC";
    case Subdetector::kNDLAr_TPC:
      return "NDLAr_TPC";
    case Subdetector::kNDLAr_PDS:
      return "NDLAr_PDS";
    case Subdetector::kND_GAr:
      return "ND_GAr";
    default:
      return "Unknown";
  }
}

DetID::Subdetector
DetID::string_to_subdetector(const std::string& typestring)
{
  if (typestring == "DAQ")
    return Subdetector::kDAQ;
  if (typestring == "HD_PDS")
    return Subdetector::kHD_PDS;
  if (typestring == "HD_TPC")
    return Subdetector::kHD_TPC;
  if (typestring == "HD_CRT")
    return Subdetector::kHD_CRT;
  if (typestring == "VD_Cathode_PDS")
    return Subdetector::kVD_CathodePDS;
  if (typestring == "VD_Membrane_PDS")
    return Subdetector::kVD_MembranePDS;
  if (typestring == "VD_Bottom_TPC")
    return Subdetector::kVD_BottomTPC;
  if (typestring == "VD_Top_TPC")
    return Subdetector::kVD_TopTPC;
  if (typestring == "NDLAr_TPC")
    return Subdetector::kNDLAr_TPC;
  if (typestring == "NDLAr_PDS")
    return Subdetector::kNDLAr_PDS;
  if (typestring == "ND_GAr")
    return Subdetector::kND_GAr;

  return Subdetector::kUnknown;
}

} // namespace dunedaq::detdataformats
