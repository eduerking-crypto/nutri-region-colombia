export type TrustTier = "medido" | "estimado" | "literatura" | "educativo";
export type VerificationStatus = "unverified" | "verified" | "rejected";

export interface Nutrient {
  nutrient: string;
  value: number;
  unit: string;
  basis: string;
  method: string | null;
  trust_tier: TrustTier;
  verification_status: VerificationStatus;
}

export interface Food {
  id: string;
  name_common: string;
  name_variants: string[];
  name_scientific: string | null;
  food_group: string;
  state: string;
  region_associations: string[];
  allergens: string[];
  trust_tier: TrustTier;
  source_id: string;
  retrieved_at: string;
  verification_status: VerificationStatus;
  notes: string | null;
  energia_kcal: number | null;
  proteina_g: number | null;
}

export interface FoodDetail extends Food {
  nutrients: Nutrient[];
  source_citation: string | null;
  allergy_conflicts: { allergen: string; kind: string; severity: string }[];
}

export interface Estado {
  version: string;
  pilot_mode: boolean;
  ai_enabled: boolean;
  rules_total: number;
  rules_approved: number;
  foods_total: number;
  recipes_total: number;
  prices_total: number;
}

export interface Profile {
  user_id: number;
  department: string | null;
  municipality: string | null;
  zone: "urbana" | "rural" | null;
  household_size: number;
  budget_weekly_cop: number | null;
  cooking_time_minutes: number | null;
  has_refrigeration: boolean;
  meals_per_day: number;
  dietary_pattern: "omnivoro" | "vegetariano" | "vegano";
  preferred_foods: string[];
  rejected_foods: string[];
  onboarding_completed: boolean;
}

export interface SafetyMessage {
  severity: string;
  code: string;
  message: string;
}

export interface AdequacyItem {
  metric: string;
  label: string;
  value: number | null;
  unit: string;
  range: [number, number];
  in_range: boolean | null;
  source: string;
  trust_tier: TrustTier;
  verification_status: string;
}

export interface Plan {
  plan_id: number | null;
  status: "ok" | "advertencia" | "requiere_profesional" | "bloqueado" | "urgencia";
  safety_messages: SafetyMessage[];
  applied_rules: string[];
  menu: Menu | null;
  nutrition_per_day: Record<string, Record<string, number>> | null;
  adequacy: AdequacyItem[] | null;
  pilot_mode: boolean;
  limitations: string[];
}

export interface Menu {
  generator: string;
  porciones: string;
  dias: { dia: number; comidas: { tipo: string; items: MenuItem[] }[] }[];
  lista_compras?: Record<string, { name: string; grams: number; food_group: string }>;
}

export interface MenuItem {
  food_id: string;
  name: string;
  food_group: string;
  grams: number;
}

export interface Rule {
  id: string;
  version: number;
  scope: string;
  name: string;
  action: string;
  message: string;
  justification: string;
  source_desc: string;
  evidence_level: string;
  status: string;
  reviewer: string | null;
  approved_at: string | null;
  pilot_mode: boolean;
}

export interface SourceInfo {
  id: string;
  name: string;
  kind: string;
  version: string;
  license: string;
  redistribution_allowed: boolean;
  access_method: string;
  url: string | null;
  citation: string | null;
  retrieved_at: string;
  notes: string | null;
}

export interface EvidenceRef {
  id: string;
  title: string;
  citation: string;
  doi: string | null;
  stable_url: string | null;
  study_type: string | null;
  relevant_finding: string | null;
  limitations: string | null;
  trust_tier: TrustTier;
  verification_status: string;
  reviewed_at: string;
}

export interface Recipe {
  id: string;
  name: string;
  variant_name: string | null;
  region: string | null;
  servings: number;
  time_minutes: number | null;
  steps: string[];
  trust_tier: TrustTier;
  source_desc: string;
  nutrition_method: string | null;
  ingredients: { food_id: string; name: string; grams: number; unit_note: string | null }[];
  nutrition_per_serving: Record<string, number> | null;
}

export interface UserMe {
  id: number;
  email: string;
  role: string;
  display_name: string | null;
  consent_version: string | null;
  created_at: string;
}

export interface Allergy {
  id: number;
  allergen: string;
  kind: string;
  severity: string;
  notes: string | null;
}

export interface HealthFlag {
  id: number;
  flag: string;
  self_reported: boolean;
  notes: string | null;
}

export interface PriceObservation {
  id: number;
  food_id: string;
  product_desc: string;
  municipality: string;
  market: string | null;
  commercial_unit: string;
  price_cop: number;
  observed_at: string;
  data_type: string;
  source_desc: string;
  confidence: string | null;
  created_by: number | null;
}

export const TRUST_LABELS: Record<TrustTier, string> = {
  medido: "Medido",
  estimado: "Estimado",
  literatura: "Literatura",
  educativo: "Educativo",
};

export const TRUST_DESCRIPTIONS: Record<TrustTier, string> = {
  medido: "Valor analítico o de tabla oficial identificable.",
  estimado: "Cálculo o aproximación con método declarado.",
  literatura: "Propiedad descrita en literatura revisada por pares.",
  educativo: "Explicación didáctica sin pretensión de dato científico.",
};

export const GROUP_LABELS: Record<string, string> = {
  cereal: "Cereales",
  legumbre: "Legumbres",
  vegetal: "Vegetales",
  fruta: "Frutas",
  lacteo: "Lácteos",
  huevo: "Huevos",
  proteina_animal: "Proteína animal",
  grasa: "Grasas y aceites",
  especia: "Especias",
  azucar: "Azúcares",
  otros: "Otros",
};

export const REGION_LABELS: Record<string, string> = {
  caribe: "Caribe",
  andina: "Andina",
  pacifico: "Pacífica",
  orinoquia: "Orinoquía",
  amazonia: "Amazonía",
  insular: "Insular",
};

export const NUTRIENT_LABELS: Record<string, string> = {
  energia: "Energía",
  proteina: "Proteína",
  grasa_total: "Grasa total",
  carbohidratos: "Carbohidratos",
  fibra: "Fibra dietaria",
  azucares: "Azúcares",
  calcio: "Calcio",
  hierro: "Hierro",
  magnesio: "Magnesio",
  fosforo: "Fósforo",
  potasio: "Potasio",
  sodio: "Sodio",
  zinc: "Zinc",
  vitamina_c: "Vitamina C",
  tiamina: "Tiamina (B1)",
  riboflavina: "Riboflavina (B2)",
  niacina: "Niacina (B3)",
  vitamina_b6: "Vitamina B6",
  folato: "Folato",
  vitamina_a_rae: "Vitamina A (RAE)",
  vitamina_e: "Vitamina E",
  vitamina_k: "Vitamina K",
  vitamina_b12: "Vitamina B12",
  grasas_saturadas: "Grasas saturadas",
  grasas_monoinsaturadas: "Grasas monoinsaturadas",
  grasas_poliinsaturadas: "Grasas poliinsaturadas",
  colesterol: "Colesterol",
  agua: "Agua",
};
