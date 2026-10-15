pub fn sound_label(bat: f64, baf: f64) -> &'static str {
    if bat > baf {
        "call"
    } else {
        "not-call"
    }
}

#[cfg(test)]
mod tests {
    use super::sound_label;

    #[test]
    fn bigger_score_is_the_sound_label() {
        assert_eq!(sound_label(0.507, 0.493), "call");
        assert_eq!(sound_label(0.03, 0.97), "not-call");
        assert_eq!(sound_label(0.5, 0.5), "not-call");
    }
}
