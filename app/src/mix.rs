pub fn sound_label(bat: f64, baf: f64) -> &'static str {
    if bat > baf {
        "call"
    } else {
        "not-call"
    }
}

pub const LAYA_MIN_PROBABILITY: f64 = 0.6;

pub fn mix_label(sound: &str, laya_choice: &str, laya_probability: f64) -> (String, String) {
    let sound = if sound.is_empty() { "not-call" } else { sound };
    if laya_probability < LAYA_MIN_PROBABILITY || laya_choice.is_empty() {
        return (sound.to_string(), "blue-a".to_string());
    }
    if laya_choice == sound {
        return (sound.to_string(), "agree".to_string());
    }
    ("review".to_string(), "disagree".to_string())
}

#[cfg(test)]
mod tests {
    use super::{mix_label, sound_label};

    #[test]
    fn bigger_score_is_the_sound_label() {
        assert_eq!(sound_label(0.507, 0.493), "call");
        assert_eq!(sound_label(0.03, 0.97), "not-call");
        assert_eq!(sound_label(0.5, 0.5), "not-call");
    }

    #[test]
    fn agreement_disagreement_and_low_probability() {
        assert_eq!(mix_label("call", "call", 0.8), ("call".to_string(), "agree".to_string()));
        assert_eq!(mix_label("not-call", "call", 0.9), ("review".to_string(), "disagree".to_string()));
        assert_eq!(mix_label("not-call", "call", 0.4), ("not-call".to_string(), "blue-a".to_string()));
    }
}
