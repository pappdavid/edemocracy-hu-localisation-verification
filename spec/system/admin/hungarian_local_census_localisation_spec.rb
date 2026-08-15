require "rails_helper"

describe "Hungarian local-census administration localisation", :admin do
  scenario "renders the screenshoted local-census form with Hungarian labels and document types" do
    visit new_admin_local_census_record_path(locale: :hu)

    expect(page).to have_content "Új helyi névjegyzék-rekord létrehozása"
    expect(page).to have_content "Okmány típusa"
    expect(page).to have_content "Okmányazonosító"
    expect(page).to have_content "Születési dátum"
    expect(page).to have_content "Irányítószám"
    expect(page).to have_select "local_census_record_document_type",
                                with_options: ["Személyi igazolvány", "Útlevél", "Lakcímkártya"]
    expect(page).not_to have_content "DNI"
    expect(page).not_to have_content "Document type"
  end
end
